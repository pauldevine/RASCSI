import time

from menu.menu_controller import MenuController
from ctrlboard_hw.hardware_button import HardwareButton
from ctrlboard_hw.encoder import Encoder
from observer import Observer


class CtrlBoardMenuUpdateEventHandler(Observer):

    def __init__(self, menu_controller: MenuController):
        self.message = None
        self._menu_controller = menu_controller

    def update(self, updated_object):
        if isinstance(updated_object, HardwareButton):
            if updated_object.name == "RotBtn":
                menu = self._menu_controller.get_active_menu()

                info_object = menu.get_current_info_object()
                self.process_scsi_id_list_context_actions(info_object)
                self.process_action_menu_actions(info_object)

                self._menu_controller.get_menu_renderer().render()
            else:
                self._menu_controller.get_menu_renderer().message = updated_object.name + " pressed!"
                self._menu_controller.get_menu_renderer().render()
                time.sleep(1)
                self._menu_controller.get_menu_renderer().message = ""
                self._menu_controller.get_menu_renderer().render()
        if isinstance(updated_object, Encoder):
            # print(updatedObject.direction)
            active_menu = self._menu_controller.get_active_menu()
            if updated_object.direction == 1:
                if active_menu.item_selection + 1 < len(active_menu.entries):
                    self._menu_controller.get_active_menu().item_selection += 1
            if updated_object.direction == -1:
                if active_menu.item_selection - 1 >= 0:
                    active_menu.item_selection -= 1
                else:
                    active_menu.item_selection = 0
            self._menu_controller.get_menu_renderer().render()

    def process_action_menu_actions(self, info_object):
        if info_object["context"] == "action_menu":
            if info_object["action"] == "return":
                self.scsi_id_list_menu_segue()
            if info_object["action"] == "slot_command_attach_insert":
                print(self._menu_controller.get_active_menu().context_object)
                self.scsi_id_list_menu_segue()
            if info_object["action"] == "slot_command_detach_eject":
                print(self._menu_controller.get_active_menu().context_object)
                self.scsi_id_list_menu_segue()
            if info_object["action"] == "slot_command_info":
                print(self._menu_controller.get_active_menu().context_object)
                self.scsi_id_list_menu_segue()
            if info_object["action"] == "load_profile":
                print(self._menu_controller.get_active_menu().context_object)
                self.scsi_id_list_menu_segue()
            if info_object["action"] == "shutdown":
                print(self._menu_controller.get_active_menu().context_object)
                self.scsi_id_list_menu_segue()

    def scsi_id_list_menu_segue(self):
        self._menu_controller.get_active_menu().context_object = None
        self._menu_controller.refresh_menu("scsi_id_menu")
        self._menu_controller.set_active_menu("scsi_id_menu")

    def process_scsi_id_list_context_actions(self, info_object):
        if info_object["context"] == "scsi_id_list_menu":
            if info_object["action"] == "open_action_menu":
                context_object = self._menu_controller.get_active_menu().get_current_info_object()
                self._menu_controller.set_active_menu("action_menu")
                self._menu_controller.get_active_menu().context_object = context_object
