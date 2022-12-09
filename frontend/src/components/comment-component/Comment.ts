import { FASTElement, observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import { Author, Like } from "../../libs/api-service/SocialApiModel";

export class Comment extends FASTElement {
    @observable
    public authorId?: string;

    @observable
    public author?: Author;

    @observable
    public published?: Date;

    @observable
    public comment?: string;

    @observable
    public commentId?: string;

    @observable
	public userId?: string;

	@observable
	public user?: Author;

    @observable
    public likes: Like[] = [];

    @observable
    public userLikedPost = false;

    @observable
    public inbox = false;

    public getPostUrl() {
        if (!this.commentId || !this.author) {
            return "/";
        }

        const postId = this.getPostId();

        const url = new URL("/view-post/" + this.getPostAuthorId() + "/" + postId, window.location.origin);
        
        return url.toString();
    }

    private getPostId() {
        if (!this.commentId) {
            return "";
        }

        const postId = this.commentId.split("/")[this.commentId.split("/").length - 4];

        return postId;
    }

    private getPostAuthorId() {
        if (!this.commentId) {
            return "";
        }  
        return this.commentId.split("/")[this.commentId.split("/").length - 6];
    } 
}