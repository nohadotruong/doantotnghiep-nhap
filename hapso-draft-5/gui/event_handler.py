from config.ui_config import MENU_ITEMS
from state.app_state import get_app_state

import pygame


class EventHandler:
    def handle_events(self, app):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                app.running = False
            elif event.type == pygame.KEYDOWN:
                if app.load_map_mode:
                    if event.key == pygame.K_q:
                        app.load_map_mode = False
                    elif event.key == pygame.K_UP:
                        app.map_selected_index = max(0, app.map_selected_index - 1)
                        if app.map_selected_index < app.map_page * app.maps_per_page:
                            app.map_page = max(0, app.map_page - 1)
                    elif event.key == pygame.K_DOWN:
                        app.map_selected_index = min(
                            len(app.map_list) - 1, app.map_selected_index + 1
                        )
                        if (
                            app.map_selected_index
                            >= (app.map_page + 1) * app.maps_per_page
                        ):
                            app.map_page += 1
                    elif event.key == pygame.K_RETURN:
                        app._load_selected_map()
                        app.load_map_mode = False
                elif event.key == pygame.K_ESCAPE:
                    app.running = False
                elif event.key in MENU_ITEMS:
                    app.current_page = event.key
                    app.selected_item = 0
                    page_name = MENU_ITEMS[event.key]
                    print(f"[EVENT_HANDLER]: SWITCHED TO: {page_name}")
                    if event.key == pygame.K_F1:
                        app.editor_status = "Obstacle"
                    elif event.key == pygame.K_F2:
                        app.editor_status = "Ready"
                    elif event.key == pygame.K_F5:
                        app._run_f5_compare()
                elif app.current_page == pygame.K_F1:
                    self._handle_f1_keyboard(app, event)
                elif app.current_page == pygame.K_F2:
                    self._handle_f2_keyboard(app, event)
                elif app.current_page == pygame.K_F3:
                    self._handle_f3_keyboard(app, event)
                elif app.current_page == pygame.K_F4:
                    self._handle_f4_keyboard(app, event)
                elif app.current_page == pygame.K_F5:
                    if event.key == pygame.K_r:
                        app._run_f5_compare()
            elif (not app.load_map_mode) and app.current_page == pygame.K_F1:
                self._handle_f1_mouse_event(app, event)
            elif app.current_page == pygame.K_F3:
                self._handle_f3_mouse_event(app, event)

    def _handle_f1_keyboard(self, app, event):
        if event.key == pygame.K_1:
            app.selected_item = 0
            app.editor_status = "Obstacle"
            print("[EVENT_HANDLER]: Mode: Obstacle")
        elif event.key == pygame.K_2:
            app.selected_item = 1
            app.editor_status = "Ecrase"
            print("[EVENT_HANDLER]: Mode: Ecrase")
        elif event.key == pygame.K_s:
            app.selected_item = 2
            app.editor_status = "Start"
            print("[EVENT_HANDLER]: Mode: Set Start point")
        elif event.key == pygame.K_g:
            app.selected_item = 3
            app.editor_status = "Goal"
            print("[EVENT_HANDLER]: Mode: Set Goal point")
        elif event.key == pygame.K_RETURN:
            app._save_map()
        elif event.key == pygame.K_l:
            app._open_load_map_ui()
        elif event.key == pygame.K_c:
            app.grid_map.clear_map()
            app.editor_status = "Clear"
            print("[EVENT_HANDLER]: Grid cleared")

    def _handle_f2_keyboard(self, app, event):
        if event.key == pygame.K_1:
            app.f2_algorithm = "A*"
            app.f2_algorithm_display = "A*"
            app.f2_remove_redundant = False
            app.f2_remove_trans_redundant = False
            app.f2_avoid_corner_cutting = False
            app.editor_status = "Algorithm: A*"
            print("[EVENT_HANDLER]: Algorithm selected: A*")
        elif event.key == pygame.K_2:
            app.f2_algorithm = "A*"
            app.f2_algorithm_display = "A* improved"
            app.f2_remove_redundant = True
            app.f2_remove_trans_redundant = True
            app.f2_avoid_corner_cutting = False
            app.editor_status = "Algorithm: A* improved (True-True-False)"
            print("[EVENT_HANDLER]: Algorithm selected: A* improved (True-True-False)")
        elif event.key == pygame.K_3:
            app.f2_algorithm = "PSO"
            app.f2_algorithm_display = "PSO"
            app.f2_use_siw = False
            app.f2_use_sobl = False
            app.editor_status = "Algorithm: PSO"
            print("[EVENT_HANDLER]: Algorithm selected: PSO")
        elif event.key == pygame.K_4:
            app.f2_algorithm = "PSO"
            app.f2_algorithm_display = "PSO improved"
            app.f2_use_siw = True
            app.f2_use_sobl = True
            app.editor_status = "Algorithm: PSO improved (SIW+SOBL)"
            print("[EVENT_HANDLER]: Algorithm selected: PSO improved (SIW+SOBL)")
        elif event.key == pygame.K_5:
            app.f2_algorithm = "APSO"
            app.f2_algorithm_display = "APSO"
            app.editor_status = "Algorithm: APSO"
            print("[EVENT_HANDLER]: Algorithm selected: APSO")
        elif event.key == pygame.K_6:
            app.f2_algorithm = "HAPSO"
            app.f2_algorithm_display = "HAPSO"
            app.editor_status = "Algorithm: HAPSO"
            print("[EVENT_HANDLER]: Algorithm selected: HAPSO")
        elif event.key == pygame.K_a:
            app.f2_algorithm = "All"
            app.f2_algorithm_display = "All Algorithms"
            app.editor_status = "Algorithm: All Algorithms"
            print("[EVENT_HANDLER]: Algorithm selected: All Algorithms")
        elif event.key == pygame.K_SPACE:
            app._run_simulation()
        elif event.key == pygame.K_RETURN:
            app._save_result()

    def _handle_f3_keyboard(self, app, event):
        if event.key == pygame.K_b:
            app.f3_algorithm = "bresenham"
            app.editor_status = "Algorithm: Bresenham"
            print("[EVENT_HANDLER]: Algorithm selected: Bresenham")
        elif event.key == pygame.K_v:
            app.f3_algorithm = "incremental"
            app.editor_status = "Algorithm: Incremental"
            print("[EVENT_HANDLER]: Algorithm selected: Incremental Traversal")
        elif event.key == pygame.K_d:
            app.f3_algorithm = "runs"
            app.editor_status = "Algorithm: Runs of Runs"
            print("[EVENT_HANDLER]: Algorithm selected: Runs of Runs")
        elif event.key == pygame.K_s:
            app.f3_algorithm = "parametric"
            app.editor_status = "Algorithm: Parametric"
            print("[EVENT_HANDLER]: Algorithm selected: Parametric (Supercover)")
        elif event.key == pygame.K_SPACE:
            app._run_line_grid_algorithm()

    def _handle_f4_keyboard(self, app, event):
        if event.key == pygame.K_SPACE:
            app._update_f4_chart()
        elif event.key == pygame.K_i:
            app.f4_input_active = "w_min"
            app.f4_input_string = ""
            print("[EVENT_HANDLER]: Input w_min: type value + ENTER")
        elif event.key == pygame.K_a:
            app.f4_input_active = "w_max"
            app.f4_input_string = ""
            print("[EVENT_HANDLER]: Input w_max: type value + ENTER")
        elif event.key == pygame.K_t:
            app.f4_input_active = "iteration"
            app.f4_input_string = ""
            print("[EVENT_HANDLER]: Input iteration: type value + ENTER")
        elif event.key == pygame.K_RETURN:
            if app.f4_input_active and app.f4_input_string:
                try:
                    val = (
                        float(app.f4_input_string)
                        if "." in app.f4_input_string
                        else int(app.f4_input_string)
                    )
                    if app.f4_input_active == "w_min":
                        app.f4_w_min = max(0.0, min(app.f4_w_max, float(val)))
                        print(f"[EVENT_HANDLER]: w_min: {app.f4_w_min:.3f}")
                    elif app.f4_input_active == "w_max":
                        app.f4_w_max = max(app.f4_w_min, min(1.0, float(val)))
                        print(f"[EVENT_HANDLER]: w_max: {app.f4_w_max:.3f}")
                    elif app.f4_input_active == "iteration":
                        app.f4_iteration = max(10, min(500, int(val)))
                        print(f"[EVENT_HANDLER]: iteration: {app.f4_iteration}")
                    app.f4_input_string = ""
                    app.f4_input_active = None
                except ValueError:
                    print("[EVENT_HANDLER]: Invalid number")
                    app.f4_input_string = ""
        elif event.key == pygame.K_BACKSPACE:
            app.f4_input_string = app.f4_input_string[:-1]
        elif event.key == pygame.K_ESCAPE:
            app.f4_input_active = None
            app.f4_input_string = ""
        elif event.unicode.isdigit() or (
            event.unicode == "." and "." not in app.f4_input_string
        ):
            if app.f4_input_active:
                app.f4_input_string += event.unicode

    def _handle_f1_mouse_event(self, app, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                app.mouse_pressed = True
                app.mouse_start_pos = event.pos
                app.mouse_current_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if app.mouse_pressed and app.grid_area:
                    end_pos = event.pos
                    app._paint_line(app.mouse_start_pos, end_pos)
                app.mouse_pressed = False
                app.mouse_start_pos = None
                app.mouse_current_pos = None
        elif event.type == pygame.MOUSEMOTION:
            if app.mouse_pressed:
                app.mouse_current_pos = event.pos

    def _handle_f3_mouse_event(self, app, event):
        return None
