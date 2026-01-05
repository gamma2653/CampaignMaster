import sys

# import pytest
from unittest import TestCase

from PySide6 import QtCore, QtTest, QtWidgets

from campaign_master.content import database as content_api
from campaign_master.content.planning import CampaignPlan
from campaign_master.gui.widgets.planning import CampaignPlanEdit

# @pytest.fixture
# def application():
#     app = QtWidgets.QApplication(sys.argv)
#     yield app
#     app.quit()

# @pytest.fixture
# def setup_content():
#     content_api.create_db_and_tables()
#     content_api.create_example_data()
#     yield


# def test_content_api():
#     [
#         setup_content
#     ]
#     campaign_plan = content_api.create_object(CampaignPlan)
#     print(campaign_plan)
#     assert campaign_plan is CampaignPlan


# def test_campaign_plan_edit():
#     window = CampaignPlanEdit()
#     # QtTest.QTest.mouseClick(window.add_button, QtCore.Qt.MouseButton.LeftButton)
#     # QtTest.QTest.keyClick(window.add_button, QtCore.Qt.Key.Enter)


class GUITestCase(TestCase):

    def setUp(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)
        content_api.create_db_and_tables()
        content_api.create_example_data()

    def tearDown(self) -> None:
        self.app.quit()
