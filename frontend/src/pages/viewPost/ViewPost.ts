import { Page } from "../Page";
import { observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import {Comment, Post} from "../../libs/api-service/SocialApiModel";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faThumbsUp, faCommentDots } from "@fortawesome/free-solid-svg-icons";



export class ViewPost extends Page {
  @observable
  public post?: Post;

  @observable
  public comments?: Comment[];

  @observable
  public commentsLoaded: boolean = false;

  @observable
  public loadedPostText: string = "";

  @observable
  public viewLikes: boolean = false;

  @observable
  public viewCreateCommentModal: boolean = false;

  @observable
  public postId?: string;

  public constructor() {
    super();
    const postId = this.getAttribute("postId");
    this.removeAttribute("postId");
    if (postId) {
      this.postId = postId;
      this.getPost(postId).then(() => {
        this.getComments()
      })
    }

    this.addIcons();
  }

  public connectedCallback() {
    super.connectedCallback();
  }

  private addIcons() {
    library.add(faThumbsUp, faCommentDots);
  }

  private async getPost(postId: string) {
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

  public async likePost() {
    if (!this.post || !this.post.author || !this.post.author.url) {
      console.error("Post must have an author with an author url");
      return;
    }

    if (!this.user || !this.user.url) {
      console.error("Current user must have a url");
      return;
    }

    try {
      const res = await SocialApi.likePost(
        this.post.id,
        this.user.id,
        this.user.url,
        this.post.author.id,
        this.post.author.url
      );
    } catch (e) {
      console.error(e);
    }
  }

  public async getComments() {
    if (!this.post || !this.post.id || !(<any>this.post.author).id) {
      console.error("Cannot get comments without the post id and the author id");
      return;
    }

    try {
      const comments = await SocialApi.getComments(
        (<any>this.post.author).id,
        this.post.id
      );
      console.log("Fetched comments:", comments);
      if (comments) {
        this.comments = comments;
        this.commentsLoaded = true
      }
    } catch (e) {
      this.commentsLoaded = false;
      console.error(e);
    }
  }

  public async toggleLikesModal() {
    console.log("Likes modal toggled, new value:", !this.viewLikes);
    this.viewLikes = !this.viewLikes
  }

  public async toggleCreateCommentModal() {
    console.log("Create comment modal toggled, new value:", !this.viewCreateCommentModal);
    this.viewCreateCommentModal = !this.viewCreateCommentModal;
  }
}
