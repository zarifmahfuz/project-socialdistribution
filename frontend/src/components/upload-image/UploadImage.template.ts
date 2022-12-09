import { html, ref, when } from "@microsoft/fast-element";
import { UploadImage } from "./UploadImage";


export const UploadImageTemplate = html<UploadImage>`
    <div class="image-form">
        <h2 class="create-post-text3">Upload an Image</h2>
        <p style="color: red;">${x => x.imageUploadError}</p>
        <form ${ref("imageForm")} @submit="${(x, c) => x.createImage(c.event)}">
            <input class="create-image-upload" type="file" name="image" accept="image/png, image/jpeg">
            <button class="create-image-button button create-post-text1 create-post-text2">Upload Image</button>
        </form>
        ${when(x => x.lastImageUrl, html<UploadImage>`
            You uploaded this image:
            <img src="${x => x.lastImageUrl}">
            <strong>[SAVE THIS FOR REFERENCE]</strong> Your uploaded image url is: <strong>${x => x.lastImageUrl}</strong>
            <button 
                class="create-image-button button create-post-text1 create-post-text2" 
                @click="${x => navigator.clipboard.writeText(x.lastImageUrl || "")}">
                Copy Image URL
            </button>
        `)}
    </div>
`;