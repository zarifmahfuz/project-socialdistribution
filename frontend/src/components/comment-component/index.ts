import { provideFASTDesignSystem } from "@microsoft/fast-components";
import { Comment } from "./Comment";
import { CommentStyles as styles } from "./Comment.styles";
import { CommentTemplate as template } from "./Comment.template";
import { ComponentEntry, defineComponent } from "../../pages/AppRegistry";

export const commentComponent = {
    name: "comment-component",
    template,
    styles,
    shadowOptions: {
        delegatesFocus: true,
    },
};

defineComponent(new ComponentEntry(commentComponent, Comment));

provideFASTDesignSystem()
    .register();


