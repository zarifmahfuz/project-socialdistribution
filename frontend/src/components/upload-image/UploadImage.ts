import { FASTElement, observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import { ImageHelpers } from "../../libs/core/Helpers";

export class UploadImage extends FASTElement {
    public imageForm?: HTMLFormElement;

    @observable
    public userId?: string;

    @observable
    public lastImageUrl?: string;

    @observable
    public imageUploadError: string = "";

    public async createImage(e: Event) {
        e.preventDefault();

        if (!this.imageForm) {
            return;
        }

        if (!this.userId) {
            return;
        }

        const formData = new FormData(this.imageForm);
        this.imageForm.reset();

        if (formData.get('image')) {
            const base64 = await ImageHelpers.convertBase64(formData.get("image"));
            if (base64 && typeof base64 === 'string') {
                const imagePostData = new FormData();
                imagePostData.set("image", base64)

                let type = "image/jpeg;base64";
                if (base64.split(",").length > 0) {
                    type = base64.split(",")[0].slice(5)
                }
                imagePostData.set("content_type", type)

                try {
                    const responseData = await SocialApi.createPost(this.userId, imagePostData);
                    if (responseData && responseData.url) {
                        this.lastImageUrl = responseData.url;
                        this.imageUploadError = ""
                    }
                } catch (e) {
                    console.warn(e)
                    this.imageUploadError = "Error uploading image"
                }
            }
        }
    }
}