from ctrlboard_menu_builder import CtrlBoardMenuBuilder
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

                self.route_rotary_button_handler(info_object)

                self._menu_controller.get_menu_renderer().render()
            else:
                self._menu_controller.show_message(updated_object.name + " pressed!")
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

    def route_rotary_button_handler(self, info_object):
        context = info_object["context"]
        action = info_object["action"]
        handler_function_name = "handle_" + context + "_" + action
        try:
            handler_function = getattr(self, handler_function_name)
            if handler_function is not None:
                handler_function(info_object)
        except AttributeError:
            print("handler function [" + str(handler_function_name) + "] not found. Skipping.")

    def handle_scsi_id_menu_openactionmenu(self, info_object):
        context_object = self._menu_controller.get_active_menu().get_current_info_object()
        self._menu_controller.segue(CtrlBoardMenuBuilder.ACTION_MENU, context_object=context_object)

    def handle_action_menu_return(self, info_object):
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def handle_action_menu_slot_attachinsert(self, info_object):
        context_object = self._menu_controller.get_active_menu().context_object
        scsi_id = context_object["scsi_id"]
        self._menu_controller.segue(CtrlBoardMenuBuilder.IMAGES_MENU, context_object=context_object)

    def handle_action_menu_slot_detacheject(self, info_object):
        self.detach_eject_scsi_id()
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def handle_action_menu_slot_info(self, info_object):
        print(self._menu_controller.get_active_menu().context_object)
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def handle_action_menu_loadprofile(self, info_object):
        print(self._menu_controller.get_active_menu().context_object)
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def handle_action_menu_shutdown(self, info_object):
        print(self._menu_controller.get_active_menu().context_object)
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def handle_images_menu_return(self, info_object):
        self._menu_controller.segue(CtrlBoardMenuBuilder.ACTION_MENU)

    def handle_images_menu_image_attachinsert(self, info_object):
        self.attach_insert_scsi_id(info_object)
        self._menu_controller.segue(CtrlBoardMenuBuilder.SCSI_ID_MENU)

    def attach_insert_scsi_id(self, info_object):
        image_name = info_object["name"]
        device_type = info_object["device_type"]
        context_object = self._menu_controller.get_active_menu().context_object
        scsi_id = context_object["scsi_id"]
        rascsi_client = self._menu_controller.get_rascsi_client()
        rascsi_client.attach_image(scsi_id=scsi_id, device_type=device_type, image=image_name)
        self.show_id_action_message(scsi_id, "attached")

    def detach_eject_scsi_id(self):
        context_object = self._menu_controller.get_active_menu().context_object
        rascsi_client = self._menu_controller.get_rascsi_client()
        scsi_id = context_object["scsi_id"]
        device_info = rascsi_client.list_devices(scsi_id)
        device_type = device_info["device_list"][0]["device_type"]
        image = device_info["device_list"][0]["image"]
        # ['SAHD', 'SCHD', 'SCRM', 'SCMO', 'SCCD', 'SCBR', 'SCDP']}
        # ['SCBR', 'SCDP']}
        if device_type == "SAHD" or device_type == "SCHD":
            result = rascsi_client.detach_by_id(scsi_id)
            self.show_id_action_message(scsi_id, "detached")
        elif device_type == "SCRM" or device_type == "SCMO" or device_type == "SCCD":
            if len(image) > 0:
                result = rascsi_client.eject_by_id(scsi_id)
                self.show_id_action_message(scsi_id, "ejected")
            else:
                result = rascsi_client.detach_by_id(scsi_id)
                self.show_id_action_message(scsi_id, "detached")
        else:
            print("device type currently unhandled!")

    def show_id_action_message(self, scsi_id, action: str):
        self._menu_controller.show_message("ID " + str(scsi_id) + " " + action + "!")

