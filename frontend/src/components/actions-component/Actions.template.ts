import { icon } from "@fortawesome/fontawesome-svg-core";
import { html, ref, repeat, when } from "@microsoft/fast-element";
import { Author } from "../../libs/api-service/SocialApiModel";
import { LayoutHelpers } from "../../libs/core/Helpers";
import { LayoutType } from "../../libs/core/PageModel";
import { authorInfo } from "../author-info";
import { Actions } from "./Actions";

authorInfo;

const PostCommentModal = html<Actions>`
    <form ${ref("form")} @submit="${(x, c) => x.postComment(c.event)}" id="comments-modal" class="${x => x.commentsModalStyle}">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-header-text">Make a comment</h2>
                <button type="button" class="close-modal" @click="${x => x.closePostCommentModal()}">
                    Close
                </button>
            </div>
            <div class="post-comment-area">
                <textarea
                    placeholder="Write your comment here..."
                    class="comment-textarea textarea"
                    name="comment"
                ></textarea>
                <button class="make-comment">Comment</button>
            </div>
        </div>
    </form>
`;

const ShareModal = html<Actions>`
    <div id="share-modal" class="${x => x.shareModalStyle}">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-header-text">Share this post</h2>
                <button type="button" class="close-modal" @click="${x => x.closeShareModal()}">
                    Close
                </button>
            </div>
            <div class="share-post-area">
                <ul>
                    ${repeat(x => x.followers, html<Author>`
                        <follower-component
                            @click="${(x, c) => c.parent.sharePost(c.event, x.id)}"
                            :profile=${x => x}
                            :user=${(x, c) => c.parent.user}
                            :layoutStyleClass=${_ => LayoutHelpers.getLayoutStyle(LayoutType.Tablet)}>
                        </follower-component>
                    `)}
                </ul>
            </div>
        </div>
    </div>
`;

export const ActionsTemplate = html<Actions>`
    ${PostCommentModal}
    ${ShareModal}
    <div class="post-actions">
        <div class="post-action-icon ${x => x.userLikedPost && x.postId ? "liked" : ""} ${x => x.userLikedComment && x.commentId ? "liked" : ""} ${x => x.commentId ? "comment-icon" : ""}" @click="${x => x.sendLike()}" :innerHTML="${_ => icon({ prefix: 'fas', iconName: "thumbs-up" }).html}"></div>
        ${when(x => !x.commentId, html<Actions>`
        <div class="post-action-icon" @click="${x => x.openPostCommentModal()}" :innerHTML="${_ => icon({ prefix: 'fas', iconName: "comment-dots" }).html}"></div>
        <div class="post-action-icon" @click="${x => x.openShareModal()}" :innerHTML="${_ => icon({ prefix: 'fas', iconName: "share" }).html}"></div>
        `)}
    </div>
`;