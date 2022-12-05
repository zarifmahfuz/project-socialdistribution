import {attr, FASTElement, observable} from "@microsoft/fast-element";
import {SocialApi} from "../../libs/api-service/SocialApi";
import serializeForm = SocialApi.serializeForm;

export class CommentModal extends FASTElement {
  @attr greeting: string = 'Comment Modal';

  @observable
  public parent: any

  public form?: HTMLFormElement;

  public connectedCallback() {
    super.connectedCallback();
  }

  public async postComment(e: Event) {
    console.log("Posting comment");

    e.preventDefault();

    if (!this.parent) {
      console.error("Parent component must be defined");
      return;
    }

    if (!this.form) {
      console.error("Form must be defined");
      return;
    }

    const form = new FormData(this.form);
    const formData = serializeForm(form);
    console.log("Comment content:", formData.comment);

    try {
      const res = await SocialApi.postComment(
        this.parent.user.id,
        this.parent.user.url,
        this.parent.post.id,
        this.parent.post.author.id,
        this.parent.post.author.url,
        formData.comment
      );
    } catch (e) {
      console.error(e);
    }
  }
}
