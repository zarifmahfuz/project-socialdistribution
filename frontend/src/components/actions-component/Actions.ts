import { library } from "@fortawesome/fontawesome-svg-core";
import { faCommentDots, faShare, faThumbsUp } from "@fortawesome/free-solid-svg-icons";
import { FASTElement, observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import { Author, Like, Comment, Post } from "../../libs/api-service/SocialApiModel";
import { SocialApiTransform } from "../../libs/api-service/SocialApiTransform";
import { ViewPost } from "../../pages/viewPost/ViewPost";

const PAGE_SIZE = 10;

export class Actions extends FASTElement {
	public form?: HTMLFormElement;

	@observable
	public postId?: string;

	@observable
	public post?: Post;

	@observable
	public postComponent?: ViewPost;

	@observable
	public profileId?: string;

	@observable
	public profile?: Author;

	@observable
	public commentId?: string;

	@observable
	public userId?: string;

	@observable
	public user?: Author;

	@observable
	public commentLikes: Like[] = [];

	@observable
	public followers: Author[] = [];

	@observable
	public comments: Comment[] = [];

	@observable
	public commentsModalStyle = "modal-close";

	@observable
	public shareModalStyle = "modal-close";

	@observable
	public userLikedComment = false;

	@observable
	public userLikedPost = false;

	constructor() {
		super();
		this.addIcons()
	}

	public connectedCallback() {
		super.connectedCallback();
		this.getCommentLikes()
	}

	private addIcons() {
		library.add(faThumbsUp, faCommentDots, faShare);
	}

	public async sharePost(e: Event, followerId: string) {
		if (!this.postId) {
			console.error("Post must have an id");
			return;
		}

		if (!this.profileId) {
			console.error("Profile must have an id");
			return;
		}

		if (!this.userId) {
			console.error("User must have an id");
			return;
		}

		if (!this.post?.author?.id || !this.post?.author?.url) {
			console.error("Post must have an author");
			return;
		}

		try {
			const response = await SocialApi.sharePost(followerId, this.postId, this.post?.author?.id, this.post?.author?.url);
			this.closeShareModal();
			if (response) {
				console.log("Post shared");
			}
		} catch (e) {
			console.error(e);
		}
	}

	public async sendLike() {
		if (!this.user || !this.user.url) {
			console.error("Current user must have a url");
			return;
		}

		try {
			let response;
			if (this.commentId) {
				if (!this.profileId) {
					console.error("Profile must have an id");
					return;
				}

				response = await SocialApi.likeComment(
					this.profileId,
					this.user.id,
					this.user.url,
					this.commentId
				)
			} else {
				if (!this.post || !this.post.author || !this.post.author.url) {
					console.error("Post must have an author with an author url");
					return;
				}

				response = await SocialApi.likePost(
					this.post.id,
					this.user.id,
					this.user.url,
					this.post.author.id,
					this.post.author.url
				)
			}
			if (response) {
				// Update post for like count
				if (this.postComponent && this.postId) {
					this.postComponent.getPost(this.postId)
					this.postComponent.getLikes()
				} else {
					// must have been a comment like
					this.getCommentLikes()
				}
			}
		} catch (e) {
			console.error(e);
		}
	}

	public async postComment(e: Event) {
		e.preventDefault();
		this.closePostCommentModal();

		if (!this.form) {
			return;
		}

		if (!this.userId || !this.postId || !this.profileId || !this.user?.url || !this.profile?.url) {
			return;
		}

		const form = new FormData(this.form);

		try {
			const responseData = await SocialApi.postComment(
				this.userId,
				this.user?.url,
				this.postId,
				this.profileId,
				this.profile?.url,
				form
			);
			if (responseData) {
				if (this.postComponent) {
					this.postComponent.getComments()
				}
			}
		} catch (e) {
			console.error(e);
		}
	}

	public async getCommentLikes() {
		if (!this.profileId) {
			console.error("User must have an id");
			return;
		}

		if (!this.commentId) {
			console.error("Comment must have an id");
			return;
		}

		try {
			const response = await SocialApi.getCommentLikes(this.commentId);
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
		this.commentLikes.splice(0, this.commentLikes.length);

		for (const data of responseData) {
			const like = SocialApiTransform.likeDataTransform(data)
			if (like) {
				this.commentLikes.push(like)
			}
		}

		// Check if user liked post
		if (!this.userId) {
			return;
		}

		this.userLikedComment = this.commentLikes.some(like => like.author?.id === this.userId);
	}

	public async getFollowers() {
		if (!this.userId) {
			return;
		}

		try {
			const responseData = await SocialApi.fetchPaginatedFollowers(this.userId, 1, PAGE_SIZE);
			if (responseData && Array.isArray(responseData)) {
				this.followers.splice(0, this.followers.length);
				for (var authorData of responseData) {
					const author = SocialApiTransform.authorDataTransform(authorData);
					if (author) {
						this.followers.push(author);
					}
				}
			}
		} catch (e) {
			console.error("Follower fetch failed", e);
		}
	}

	public async openPostCommentModal() {
		this.commentsModalStyle = "modal-open";
		if (this.postComponent) {
			await this.postComponent.getComments()
		}
	}

	public closePostCommentModal() {
		this.commentsModalStyle = "modal-close";
	}

	public async openShareModal() {
		this.shareModalStyle = "modal-open";
		await this.getFollowers();
	}

	public closeShareModal() {
		this.shareModalStyle = "modal-close";
	}
}