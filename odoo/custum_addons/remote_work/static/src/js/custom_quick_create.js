/** @odoo-module **/

import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

export class CustomQuickCreate extends Component {
    setup() {
    console.log("testing into custum quik create")
        this.notification = useService("notification");
        this.state = useState({
            title: this.props.record.title || "",
            date: this.props.record.start || DateTime.now(),
        });
    }

    save() {
        if (!this.state.title.trim()) {
            this.notification.add(_t("Please enter a title"), { type: 'danger' });
            return;
        }

        const record = {
            ...this.props.record,
            title: this.state.title,
            start: this.state.date,
            end: this.state.date,
        };

        this.props.editRecord(record);
        this.props.close();
    }
}

CustomQuickCreate.template = "remote_work.CustomQuickCreate";
CustomQuickCreate.props = {
    record: Object,
    editRecord: Function,
    close: Function,
    title: { type: String, optional: true },
};