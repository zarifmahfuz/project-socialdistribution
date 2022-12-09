import { provideFASTDesignSystem } from "@microsoft/fast-components";
import { ComponentEntry, defineComponent } from "../../pages/AppRegistry";
import { UploadImage } from "./UploadImage";
import { UploadImageStyles as styles } from "./UploadImage.styles";
import { UploadImageTemplate as template } from "./UploadImage.template";

export const uploadImage = {
    name: "upload-image",
    template,
    styles,
    shadowOptions: {
        delegatesFocus: true,
    },
};

defineComponent(new ComponentEntry(uploadImage, UploadImage));

provideFASTDesignSystem()
    .register();


