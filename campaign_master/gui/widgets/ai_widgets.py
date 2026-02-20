"""
AI-enabled text input widgets with inline ghost text completion support.

Provides AILineEdit and AITextEdit widgets that automatically show AI-powered
ghost text completion 600ms after the user stops typing. Press Enter to accept,
Escape or any other key to dismiss.
"""

from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

from campaign_master.ai import AICompletionService, CompletionResponse
from campaign_master.util import get_basic_logger

logger = get_basic_logger(__name__)


class AILineEdit(QtWidgets.QLineEdit):
    """
    QLineEdit with inline AI ghost text completion.

    After 600ms of inactivity, an AI completion appears as faint ghost text
    after the cursor. Press Enter to accept, Escape or any other key to dismiss.
    """

    completionRequested = QtCore.Signal()
    completionReceived = QtCore.Signal(str)

    def __init__(
        self,
        text: str = "",
        field_name: str = "",
        entity_type: str = "",
        entity_context_func=None,
        placeholder: str = "",
        parent=None,
    ):
        """
        Initialize the AI-enabled line edit.

        Args:
            text: Initial text content
            field_name: Name of the field (for AI context)
            entity_type: Type of entity being edited (for AI context)
            entity_context_func: Callable that returns entity data dict
            placeholder: Placeholder text shown when field is empty
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.field_name = field_name
        self.entity_type = entity_type
        self._entity_context_func = entity_context_func
        self._loading = False

        self._ghost_text: str = ""
        self._ghost_full_text: str = ""
        self._modifying_ghost: bool = False

        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(600)
        self._debounce_timer.timeout.connect(self.trigger_completion)

        self.textChanged.connect(self._on_text_changed)

        if placeholder:
            self.setPlaceholderText(placeholder)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle ghost text acceptance/dismissal and normal key input."""
        if self._ghost_text:
            if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Tab):
                self._accept_ghost()
                return
            elif event.key() == QtCore.Qt.Key.Key_Escape:
                self._clear_ghost()
                return
            else:
                self._clear_ghost()
        super().keyPressEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent):
        """Clear ghost text and stop debounce timer when focus is lost."""
        self._clear_ghost()
        self._debounce_timer.stop()
        super().focusOutEvent(event)

    def _on_text_changed(self):
        """Restart debounce timer on text change; clear any existing ghost."""
        if self._modifying_ghost or not self.hasFocus():
            return
        self._ghost_text = ""
        self._ghost_full_text = ""
        self.update()
        self._debounce_timer.stop()
        if len(self.text()) >= 3:
            self._debounce_timer.start()

    def trigger_completion(self):
        """Request AI completion for current text."""
        logger.debug("Requesting AI completion for field '%s'", self.field_name)
        service = AICompletionService.instance()

        if not service.is_enabled():
            return

        if self._loading:
            return

        self._loading = True
        self.setCursor(QtCore.Qt.CursorShape.WaitCursor)

        entity_ctx = {}
        if self._entity_context_func:
            try:
                entity_ctx = self._entity_context_func()
            except Exception:
                logger.exception("Error obtaining entity context")

        context: dict[str, Any] = {
            "campaign": entity_ctx.get("campaign", {}),
            "entity": {
                "obj_id": entity_ctx.get("obj_id", {}),
                "field": self.field_name,
                "current_value": self.text(),
            },
        }

        self.completionRequested.emit()

        logger.debug("Sending completion request to AI service")
        service.complete_async(
            prompt=self.text(),
            context=context,
            callback=self._on_completion_received,
        )

    def _on_completion_received(self, response: CompletionResponse | None):
        """Handle completion response from AI service."""
        logger.debug("AI completion response received")
        self._loading = False
        self.setCursor(QtCore.Qt.CursorShape.IBeamCursor)

        if not self.hasFocus():
            return

        if not response or response.finish_reason == "error":
            if response and response.error_message:
                logger.warning("Completion error: %s", response.error_message)
            return

        if not response.text.strip():
            return

        self.completionReceived.emit(response.text)
        self._show_ghost(response.text)

    def _show_ghost(self, text: str):
        """Display ghost text suffix after the current cursor position."""
        current = self.text()
        if text.startswith(current):
            ghost_suffix = text[len(current):]
        else:
            ghost_suffix = (" " + text) if current else text
        self._ghost_full_text = text
        self._ghost_text = ghost_suffix
        self.setCursorPosition(len(self.text()))
        self.update()

    def _clear_ghost(self):
        """Remove ghost text without affecting real content."""
        self._ghost_text = ""
        self._ghost_full_text = ""
        self.update()

    def _accept_ghost(self):
        """Accept the ghost text and commit it as real content."""
        if not self._ghost_full_text:
            return
        current = self.text()
        full = self._ghost_full_text
        new_text = full if full.startswith(current) else (current + " " + full).strip()
        self._modifying_ghost = True
        try:
            self.setText(new_text.strip())
            self.setCursorPosition(len(self.text()))
        finally:
            self._modifying_ghost = False
        self._clear_ghost()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Paint the widget, then overlay ghost text after the real content."""
        super().paintEvent(event)
        if not self._ghost_text:
            return
        if self.cursorPosition() != len(self.text()):
            return
        painter = QtGui.QPainter(self)
        painter.setFont(self.font())
        color = self.palette().color(QtGui.QPalette.ColorRole.Text)
        color.setAlphaF(0.40)
        painter.setPen(color)
        rect = self.cursorRect()
        fm = QtGui.QFontMetrics(self.font())
        cr = self.contentsRect()
        text_y = cr.top() + (cr.height() - fm.height()) // 2 + fm.ascent()
        painter.drawText(QtCore.QPoint(rect.x(), text_y), self._ghost_text)
        painter.end()


class AITextEdit(QtWidgets.QTextEdit):
    """
    QTextEdit with inline AI ghost text completion.

    After 600ms of inactivity, an AI completion appears as faint ghost text
    inserted at the end of the document. Press Enter to accept, Escape or any
    other key to dismiss. toPlainText() always returns text without the ghost
    suffix so callers always receive clean content.

    This widget is sized larger than standard text edits for multi-line content.
    """

    completionRequested = QtCore.Signal()
    completionReceived = QtCore.Signal(str)

    def __init__(
        self,
        text: str = "",
        field_name: str = "",
        entity_type: str = "",
        entity_context_func=None,
        placeholder: str = "",
        parent=None,
    ):
        """
        Initialize the AI-enabled text edit.

        Args:
            text: Initial text content
            field_name: Name of the field (for AI context)
            entity_type: Type of entity being edited (for AI context)
            entity_context_func: Callable that returns entity data dict
            placeholder: Placeholder text shown when field is empty
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.field_name = field_name
        self.entity_type = entity_type
        self._entity_context_func = entity_context_func
        self._loading = False

        self._ghost_text: str = ""
        self._ghost_start_pos: int = -1
        self._modifying_ghost: bool = False

        self._debounce_timer = QtCore.QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(600)
        self._debounce_timer.timeout.connect(self.trigger_completion)

        self.textChanged.connect(self._on_text_changed)

        # Ensure text areas start at a usable height and can grow
        self.setMinimumHeight(80)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        if placeholder:
            self.setPlaceholderText(placeholder)

    def toPlainText(self) -> str:
        """Return plain text content, stripping any ghost suffix."""
        full = super().toPlainText()
        if self._ghost_text and full.endswith(self._ghost_text):
            return full[: -len(self._ghost_text)]
        return full

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle ghost text acceptance/dismissal and normal key input."""
        if self._ghost_text:
            if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
                self._accept_ghost()
                return
            elif event.key() == QtCore.Qt.Key.Key_Escape:
                self._clear_ghost()
                return
            else:
                self._clear_ghost()
        super().keyPressEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent):
        """Clear ghost text and stop debounce timer when focus is lost."""
        self._clear_ghost()
        self._debounce_timer.stop()
        self.viewport().setCursor(QtCore.Qt.CursorShape.IBeamCursor)
        super().focusOutEvent(event)

    def _on_text_changed(self):
        """Restart debounce timer on text change; clear any existing ghost."""
        if self._modifying_ghost or not self.hasFocus():
            return
        if self._ghost_text:
            self._clear_ghost()
        self._debounce_timer.stop()
        if len(super().toPlainText()) >= 3:
            self._debounce_timer.start()

    def trigger_completion(self):
        """Request AI completion for current text."""
        service = AICompletionService.instance()

        if not service.is_enabled():
            return

        if self._loading:
            return

        self._loading = True
        self.viewport().setCursor(QtCore.Qt.CursorShape.WaitCursor)

        entity_ctx = {}
        if self._entity_context_func:
            try:
                entity_ctx = self._entity_context_func()
            except Exception:
                logger.exception("Error obtaining entity context")

        context: dict[str, Any] = {
            "campaign": entity_ctx.get("campaign", {}),
            "entity": {
                "obj_id": entity_ctx.get("obj_id", {}),
                "field": self.field_name,
                "current_value": self.toPlainText(),
            },
        }

        self.completionRequested.emit()

        logger.debug("Sending completion request to AI service")
        service.complete_async(
            prompt=self.toPlainText(),
            context=context,
            callback=self._on_completion_received,
        )

    def _on_completion_received(self, response: CompletionResponse | None):
        """Handle completion response from AI service."""
        logger.debug("AI completion response received")
        self._loading = False
        self.viewport().setCursor(QtCore.Qt.CursorShape.IBeamCursor)

        if not self.hasFocus():
            return

        if not response or response.finish_reason == "error":
            if response and response.error_message:
                logger.warning("Completion error: %s", response.error_message)
            return
        logger.debug("AI completion finished with reason: %s", response.finish_reason)

        if not response.text.strip():
            return

        self.completionReceived.emit(response.text)
        logger.debug("Showing inline ghost text")
        self._show_ghost(response.text)

    def _show_ghost(self, text: str):
        """Insert ghost text into the document with a dim foreground color."""
        if self._ghost_text:
            self._clear_ghost()
        current = super().toPlainText()
        ghost_suffix = text[len(current):] if text.startswith(current) else (" " + text if current else text)
        if not ghost_suffix:
            return
        self._modifying_ghost = True
        try:
            cursor = self.textCursor()
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
            self._ghost_start_pos = cursor.position()
            fmt = QtGui.QTextCharFormat()
            color = self.palette().color(QtGui.QPalette.ColorRole.Text)
            color.setAlphaF(0.40)
            fmt.setForeground(QtGui.QBrush(color))
            cursor.insertText(ghost_suffix, fmt)
            self._ghost_text = ghost_suffix
            cursor.setPosition(self._ghost_start_pos)
            self.setTextCursor(cursor)
        finally:
            self._modifying_ghost = False

    def _clear_ghost(self):
        """Remove ghost text from the document without affecting real content."""
        if not self._ghost_text or self._ghost_start_pos < 0:
            self._ghost_text = ""
            self._ghost_start_pos = -1
            return
        self._modifying_ghost = True
        try:
            cursor = QtGui.QTextCursor(self.document())
            cursor.setPosition(self._ghost_start_pos)
            cursor.movePosition(
                QtGui.QTextCursor.MoveOperation.End,
                QtGui.QTextCursor.MoveMode.KeepAnchor,
            )
            cursor.removeSelectedText()
        finally:
            self._ghost_text = ""
            self._ghost_start_pos = -1
            self._modifying_ghost = False

    def _accept_ghost(self):
        """Accept the ghost text by reformatting it with the default character format."""
        if not self._ghost_text or self._ghost_start_pos < 0:
            return
        self._modifying_ghost = True
        try:
            cursor = QtGui.QTextCursor(self.document())
            cursor.setPosition(self._ghost_start_pos)
            cursor.movePosition(
                QtGui.QTextCursor.MoveOperation.End,
                QtGui.QTextCursor.MoveMode.KeepAnchor,
            )
            ghost = self._ghost_text
            cursor.removeSelectedText()
            cursor.insertText(ghost, QtGui.QTextCharFormat())
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
        finally:
            self._ghost_text = ""
            self._ghost_start_pos = -1
            self._modifying_ghost = False
