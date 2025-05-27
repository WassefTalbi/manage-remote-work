/** @odoo-module **/

import { CalendarCommonRenderer } from "@web/views/calendar/calendar_common/calendar_common_renderer";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(CalendarCommonRenderer.prototype, {
    setup() {
        super.setup();
        this.pastDatesDisabled = true;
        this.notification = useService("notification");
    },

    onDayRender(info) {
        super.onDayRender(info);
        if (this.pastDatesDisabled) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const cellDate = new Date(info.date);
            if (cellDate < today) {
                info.el.style.opacity = '0.6';
                info.el.style.pointerEvents = 'auto';
                info.el.style.cursor = 'not-allowed';
                info.el.addEventListener('click', (ev) => {
                    ev.stopPropagation();
                    ev.preventDefault();
                });
            }
        }
    },

    async onDateClick(info) {
        const clickedDate = new Date(info.date);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (this.pastDatesDisabled && clickedDate < today) {
            this.notification.add(_t("You cannot select a past date."), {
                type: "danger",
            });
            return;
        }
        return super.onDateClick(info);
    },
});
