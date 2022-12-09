import { provideFASTDesignSystem } from "@microsoft/fast-components";
import { Like } from "./Like";
import { LikeStyles as styles } from "./Like.styles";
import { LikeTemplate as template } from "./Like.template";
import { ComponentEntry, defineComponent } from "../../pages/AppRegistry";

export const likeComponent = {
    name: "like-component",
    template,
    styles,
    shadowOptions: {
        delegatesFocus: true,
    },
};

defineComponent(new ComponentEntry(likeComponent, Like));

provideFASTDesignSystem()
    .register();


