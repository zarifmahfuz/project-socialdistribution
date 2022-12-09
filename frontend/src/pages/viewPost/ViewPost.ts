import { Page } from "../Page";
import { observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import { Comment, Like, Post } from "../../libs/api-service/SocialApiModel";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faThumbsUp, faCommentDots } from "@fortawesome/free-solid-svg-icons";
import { SocialApiTransform } from "../../libs/api-service/SocialApiTransform";



export class ViewPost extends Page {
	public form?: HTMLFormElement;

	@observable
	public post?: Post;

	public readonly postId: string | null;

	@observable
	public comments: Comment[] = [];

	@observable
	public likes: Like[] = [];

	@observable
	public loadedPostText: string = "";

	@observable
	public likesModalStyle = "modal-close";

	@observable
	public commentsModalStyle = "modal-close";

	@observable
	public userLikedPost = false;

	public constructor() {
		super();
		this.postId = null;
		const postId = this.getAttribute("postId");
		this.removeAttribute("postId");
		if (postId) {
			this.postId = postId;
			this.getPost(postId)
		}

		this.addIcons();
	}

	public connectedCallback() {
		super.connectedCallback();
		this.getComments()
		this.getLikes()
	}

	private addIcons() {
		library.add(faThumbsUp, faCommentDots);
	}

	public async getPost(postId: string) {
		if (!this.profileId) {
			return;
		}

		try {
			const post = await SocialApi.fetchPost(postId, this.profileId);
			if (post) {
				this.post = post;
			}
		} catch (e) {
			console.error(e);
			this.loadedPostText = "Post not found.";
		}

		console.log("loaded", this.post?.id, this.user)
	}

	public async getComments() {
		if (!this.postId || !this.profileId) {
			console.error("Cannot get comments without the post id and the author id");
			return;
		}

		try {
			const comments = await SocialApi.getComments(this.profileId, this.postId);
			if (comments) {
				this.setComments(comments)
			}
		} catch (e) {
			console.error(e);
		}
	}

	public async setComments(responseData: any) {
		if (!responseData) {
			return;
		}

		// Clear comments
		this.comments.splice(0, this.likes.length);

		for (const data of responseData) {
			const comment = SocialApiTransform.commentDataTransform(data)
			if (comment) {
				this.comments.push(comment)
			}
		}
	}

	public async getLikes() {
		if (!this.postId) {
			console.error("Post must have an id");
			return;
		}

		if (!this.profileId) {
			console.error("User must have an id");
			return;
		}

		try {
			const response = await SocialApi.getPostLikes(this.postId, this.profileId);
			if (response) {
				this.setLikes(response)
			}
		} catch (e) {
			console.error(e);
		}
	}

	private setLikes(responseData: any) {
		if (!responseData) {
			return;
		}

		// Clear likes
		this.likes.splice(0, this.likes.length);

		for (const data of responseData) {
			const like = SocialApiTransform.likeDataTransform(data)
			if (like) {
				this.likes.push(like)
			}
		}

		// Check if user liked post
		if (!this.userId) {
			return;
		}

		this.userLikedPost = this.likes.some(like => like.author?.id === this.userId);
	}

	public async openLikesModal() {
		this.likesModalStyle = "modal-open";
		this.getLikes();
	}

	public closeLikesModal() {
		this.likesModalStyle = "modal-close";
	}
}