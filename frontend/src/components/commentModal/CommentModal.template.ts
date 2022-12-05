import { html, ref } from "@microsoft/fast-element";
import { CommentModal } from "./CommentModal";


export const CommentModalTemplate = html<CommentModal>`
    <div>
        <div class="comment-container">
            <div class="comment-banner"><h1 class="comment-text">Comment</h1></div>
            <form ${ref("form")}>
                            <textarea
                                    placeholder="Content"
                                    class="comment-textarea textarea"
                                    name="comment"
                            ></textarea>
                <button
                        class="comment-button button"
                        @click="${(x, c) => {
                            x.parent.toggleCreateCommentModal();
                            x.postComment(c.event);
                        }}">
                    <span>Post</span>
                </button>
            </form>
        </div>
    </div>
`;
