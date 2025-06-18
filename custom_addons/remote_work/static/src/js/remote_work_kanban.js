/** @odoo-module **/

import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";



patch(KanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.userService = useService("user");

    },
    get canMoveRecords() {
       if (this.userService.isAdmin){
        return super.canMoveRecords;
       }
    }

});