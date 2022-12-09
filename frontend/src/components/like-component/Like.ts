import { FASTElement, observable } from "@microsoft/fast-element";
import { Author } from "../../libs/api-service/SocialApiModel";

export class Like extends FASTElement {
    @observable
    public authorId?: string;

    @observable
    public author?: Author

    @observable
    public post?: string;

    @observable
    public comment?: string;

    @observable
    public userId?: string;

    @observable
    public layoutStyleClass: string = "";

    public getPostUrl() {
        if (!this.author) {
            return "/";
        }

        let postId = "";
        if (this.comment) {
            postId = this.comment.split("/")[this.comment.split("/").length - 4];
        } else if (this.post) {
            postId = this.post.split("/")[this.post.split("/").length - 2];
        }

        if (!postId) {
            return "/";
        }

        const url = new URL("/view-post/" + this.getPostAuthorId(this.comment, this.post) + "/" + postId, window.location.origin);
        
        return url.toString();
    }

    private getPostAuthorId(commentId?: string, postId?: string) {
        if (commentId) {
            return commentId.split("/")[commentId.split("/").length - 6];
        } else if (postId) {
            return this.userId;
        }
    }
}