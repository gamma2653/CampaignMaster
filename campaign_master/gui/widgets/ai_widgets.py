"""
AI-enabled text input widgets with completion support.

Provides AILineEdit and AITextEdit widgets that support AI-powered
text completion triggered by Ctrl+Space.
"""

from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets

from campaign_master.ai import AICompletionService, CompletionResponse
from campaign_master.util import get_basic_logger

logger = get_basic_logger(__name__)


class CompletionPopup(QtWidgets.QWidget):
    """
    Popup widget for displaying AI completion suggestions.

    Shows the suggested completion text with accept/reject options.
    """

    accepted = QtCore.Signal(str)
    rejected = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowType.Popup)
        self.setMinimumWidth(300)
        self.setMaximumWidth(600)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Completion text display
        self.completion_text = QtWidgets.QLabel()
        self.completion_text.setWordWrap(True)
        self.completion_text.setStyleSheet(
            """
            QLabel {
                background-color: #2d2d2d;
                color: #a0ffa0;
                padding: 8px;
                border-radius: 4px;
                font-family: monospace;
            }
        """
        )
        layout.addWidget(self.completion_text)

        # Hint text
        hint = QtWidgets.QLabel("Tab/Enter to accept, Escape to reject")
        hint.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(hint)

        self._completion = ""

    def show_completion(self, text: str, parent_widget: QtWidgets.QWidget):
        """Show the popup with the given completion text."""
        self._completion = text

        # Truncate if too long
        display_text = text
        if len(text) > 500:
            display_text = text[:500] + "..."

        self.completion_text.setText(display_text)
        self.adjustSize()

        # Position below the parent widget
        pos = parent_widget.mapToGlobal(QtCore.QPoint(0, parent_widget.height()))
        self.move(pos)
        self.show()
        self.setFocus()

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle keyboard input for accept/reject."""
        if event.key() in (QtCore.Qt.Key.Key_Tab, QtCore.Qt.Key.Key_Return):
            self.accepted.emit(self._completion)
            self.hide()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.rejected.emit()
            self.hide()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent):
        """Hide popup when focus is lost."""
        self.rejected.emit()
        self.hide()
        super().focusOutEvent(event)


class AILineEdit(QtWidgets.QLineEdit):
    """
    QLineEdit with AI completion support.

    Trigger completion with Ctrl+Space. The widget will show a popup
    with the AI suggestion that can be accepted or rejected.
    """

    completionRequested = QtCore.Signal()
    completionReceived = QtCore.Signal(str)

    def __init__(
        self,
        text: str = "",
        field_name: str = "",
        entity_type: str = "",
        entity_context_func=None,
        parent=None,
    ):
        """
        Initialize the AI-enabled line edit.

        Args:
            text: Initial text content
            field_name: Name of the field (for AI context)
            entity_type: Type of entity being edited (for AI context)
            entity_context_func: Callable that returns entity data dict
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.field_name = field_name
        self.entity_type = entity_type
        self._entity_context_func = entity_context_func
        self._popup: CompletionPopup | None = None
        self._loading = False

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle Ctrl+Space for completion trigger."""
        if event.key() == QtCore.Qt.Key.Key_Space and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            logger.debug("Ctrl+Space detected, triggering AI completion")
            self.trigger_completion()
            return
        super().keyPressEvent(event)

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

        # Build context
        context: dict[str, Any] = {
            "field_name": self.field_name,
            "entity_type": self.entity_type,
            "current_text": self.text(),
        }

        if self._entity_context_func:
            try:
                context["entity_data"] = self._entity_context_func()
            except Exception:
                logger.exception("Error obtaining entity context")
                pass

        self.completionRequested.emit()

        # Perform async completion
        logger.debug("Sending completion request to AI service")
        service.complete_async(
            prompt=self.text(),
            context=context,
            callback=self._on_completion_received,
        )

    def _on_completion_received(self, response: CompletionResponse | None):
        """Handle completion response."""
        logger.debug("AI completion response received")
        self._loading = False
        self.setCursor(QtCore.Qt.CursorShape.IBeamCursor)

        if not response or response.finish_reason == "error":
            if response and response.error_message:
                logger.warning("Completion error: %s", response.error_message)
            return

        if not response.text.strip():
            return

        self.completionReceived.emit(response.text)
        self._show_completion_popup(response.text)

    def _show_completion_popup(self, text: str):
        """Show popup with suggested completion."""
        if not self._popup:
            self._popup = CompletionPopup()
            self._popup.accepted.connect(self._accept_completion)
            self._popup.rejected.connect(self._reject_completion)

        self._popup.show_completion(text, self)

    def _accept_completion(self, text: str):
        """Accept and insert the completion."""
        current = self.text()
        # If completion looks like a continuation, append it
        if not text.startswith(current):
            new_text = current + " " + text if current else text
        else:
            new_text = text
        self.setText(new_text.strip())
        self.setFocus()

    def _reject_completion(self):
        """Reject the completion and return focus."""
        self.setFocus()


class AITextEdit(QtWidgets.QTextEdit):
    """
    QTextEdit with AI completion support.

    Trigger completion with Ctrl+Space. The widget will show a popup
    with the AI suggestion that can be accepted or rejected.

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
        parent=None,
    ):
        """
        Initialize the AI-enabled text edit.

        Args:
            text: Initial text content
            field_name: Name of the field (for AI context)
            entity_type: Type of entity being edited (for AI context)
            entity_context_func: Callable that returns entity data dict
            parent: Parent widget
        """
        super().__init__(text, parent)
        self.field_name = field_name
        self.entity_type = entity_type
        self._entity_context_func = entity_context_func
        self._popup: CompletionPopup | None = None
        self._loading = False

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Handle Ctrl+Space for completion trigger."""
        if event.key() == QtCore.Qt.Key.Key_Space and event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            logger.debug("Ctrl+Space detected, triggering AI completion")
            self.trigger_completion()
            return
        super().keyPressEvent(event)

    def trigger_completion(self):
        """Request AI completion for current text."""
        service = AICompletionService.instance()

        if not service.is_enabled():
            return

        if self._loading:
            return

        self._loading = True
        self.viewport().setCursor(QtCore.Qt.CursorShape.WaitCursor)

        # Build context
        context: dict[str, Any] = {
            "field_name": self.field_name,
            "entity_type": self.entity_type,
            "current_text": self.toPlainText(),
        }

        if self._entity_context_func:
            try:
                context["entity_data"] = self._entity_context_func()
            except Exception:
                logger.exception("Error obtaining entity context")
                pass

        self.completionRequested.emit()

        logger.debug("Sending completion request to AI service")
        # Perform async completion
        service.complete_async(
            prompt=self.toPlainText(),
            context=context,
            callback=self._on_completion_received,
        )

    def _on_completion_received(self, response: CompletionResponse | None):
        """Handle completion response."""
        logger.debug("AI completion response received")
        self._loading = False
        self.viewport().setCursor(QtCore.Qt.CursorShape.IBeamCursor)
        if not response or response.finish_reason == "error":
            if response and response.error_message:
                logger.warning("Completion error: %s", response.error_message)
            return
        logger.debug("AI completion finished with reason: %s", response.finish_reason)

        if not response.text.strip():
            return

        self.completionReceived.emit(response.text)
        logger.debug("Showing completion popup")
        self._show_completion_popup(response.text)

    def _show_completion_popup(self, text: str):
        """Show popup with suggested completion."""
        if not self._popup:
            self._popup = CompletionPopup()
            self._popup.accepted.connect(self._accept_completion)
            self._popup.rejected.connect(self._reject_completion)

        self._popup.show_completion(text, self)

    def _accept_completion(self, text: str):
        """Accept and insert the completion."""
        current = self.toPlainText()
        # If completion looks like a continuation, append it
        if not text.startswith(current):
            new_text = current + " " + text if current else text
        else:
            new_text = text
        self.setPlainText(new_text.strip())
        # Move cursor to end
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.setFocus()

    def _reject_completion(self):
        """Reject the completion and return focus."""
        self.setFocus()
