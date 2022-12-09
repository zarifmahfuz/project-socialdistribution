import { provideFASTDesignSystem } from "@microsoft/fast-components";
import { Actions } from "./Actions";
import { ActionsStyles as styles } from "./Action.styles";
import { ActionsTemplate as template } from "./Actions.template";
import { ComponentEntry, defineComponent } from "../../pages/AppRegistry";

export const actionsComponent = {
    name: "actions-component",
    template,
    styles,
    shadowOptions: {
        delegatesFocus: true,
    },
};

defineComponent(new ComponentEntry(actionsComponent, Actions));

provideFASTDesignSystem()
    .register();


