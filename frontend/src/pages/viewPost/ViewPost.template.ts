import { icon } from "@fortawesome/fontawesome-svg-core";
import { html, ref, repeat, when } from "@microsoft/fast-element";
import { layoutComponent } from "../../components/base-layout";
import { ContentType, Comment } from "../../libs/api-service/SocialApiModel";
import { LayoutHelpers } from "../../libs/core/Helpers";
import { ViewPost } from "./ViewPost";
import { authorInfo } from "../../components/author-info";
import { commentComponent } from "../../components/comment-component";

layoutComponent;
authorInfo;
commentComponent;

const LikesModal = html<ViewPost>`
    <div id="likes-modal" class="${x => x.likesModalStyle}">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-header-text">Liked by</h2>
                <button class="close-modal" @click="${x => x.closeLikesModal()}">
                    Close
                </button>
            </div>
            <ul>
                ${repeat(x => x.likes || [], html`
                    <follower-component
                        :profile=${x => x.author}
                        :user=${(x, c) => c.parent.user}
                        :layoutStyleClass="${(x, c) => LayoutHelpers.getLayoutStyle(c.parent.layoutType)}">
                    </follower-component>
                `)}
            </ul>
        </div>
    </div>
`;

export const ViewPostPageTemplate = html<ViewPost>`
    <page-layout
        :userId="${x => x.userId}"
        :user="${x => x.user}"
        :layoutType="${x => x.layoutType}"
        :layoutStyleClass="${x => LayoutHelpers.getLayoutStyle(x.layoutType)}">
        ${LikesModal}
        ${when(x => x.post, html<ViewPost>`
        <div class="post-container">
            <div class="post-container1">
                <div class="post-container2">
                    <h2><u>${x => x.post?.title}</u></h2>
                    ${when(x => x.post?.contentType == ContentType.Markdown && import('../../components/markdown-component'), html<ViewPost>`
                        <markdown-component
                            :content=${x => x.post?.content}
                        ></markdown-component>
                    `)}
                    ${when(x => x.post?.contentType == ContentType.Plain, html<ViewPost>`
                        <span class="post-text">${x => x.post?.content}</span>
                    `)}
                    <div class="post-container3">
                        <div class="post-information">
                            <author-info
                                :authorId=${x => x.post?.author?.id}
                                :author=${x => x.post?.author}
                                :published=${x => x.post?.published}
                            ></author-info>
                            <div class="see-likes" @click="${x => x.openLikesModal()}">
                                See <strong>${x => x.post?.likes}</strong> Likes
                            </div>
                        </div>
                        <actions-component
                            :userId=${x => x.userId}
                            :postId=${x => x.postId}
                            :profileId=${x => x.profileId}
                            :post=${x => x.post}
                            :user=${x => x.user}
                            :profile=${x => x.profile}
                            :postComponent=${x => x}
                            :userLikedPost=${x => x.userLikedPost}>
                        </actions-component>
                    </div>
                </div>
            </div>
            ${when(x => x.userId == x.profileId, html<ViewPost>`
                <a class="edit-post-button" href="/edit-post/${x => x.userId}/${x => x.post?.id}">Edit Post</a>
            `)}
            <ul class="comments-box">
                ${repeat(x => x.comments, html<Comment>`
                <comment-component
                    :comment=${x => x.comment}
                    :author=${x => x.author}
                    :authorId=${x => x.author?.id}
                    :published=${x => x.published}
                    :commentId=${x => x.id}
                    :user=${(x, c) => c.parent.user}
                    :userId=${(x, c) => c.parent.userId}>
                </comment-component>`
                )}
            </ul>
        </div>
        `)}
        ${when(x => !x.post, html<ViewPost>`
            <h1>${x => x.loadedPostText}</h1>
        `)}
        <div class="margin-bottom"></div>
    </page-layout>
`;
