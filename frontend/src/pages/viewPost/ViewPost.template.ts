import { icon } from "@fortawesome/fontawesome-svg-core";
import {html, repeat, when} from "@microsoft/fast-element";
import { layoutComponent } from "../../components/base-layout";
import { markdownComponent } from "../../components/markdown-component";
import {Comment, ContentType} from "../../libs/api-service/SocialApiModel";
import { LayoutHelpers } from "../../libs/core/Helpers";
import { ViewPost } from "./ViewPost";
import {likesModalComponent} from "../../components/likesModal";
import {commentModalComponent} from "../../components/commentModal";

commentModalComponent;
likesModalComponent;
layoutComponent;
markdownComponent;

export const ViewPostPageTemplate = html<ViewPost>`
    <page-layout
        :userId="${x => x.userId}"
        :user="${x => x.user}"
        :layoutType="${x => x.layoutType}"
        :layoutStyleClass="${x => LayoutHelpers.getLayoutStyle(x.layoutType)}">
        ${when(x => x.post, html<ViewPost>`
            <div class="post-container">
                <div class="post-container1">
                    <img
                            src="https://play.teleporthq.io/static/svg/default-img.svg"
                            alt="post image"
                            class="post-image"
                    />
                    <div class="post-container2">
                        ${when(x => x.post?.contentType == ContentType.Markdown, html<ViewPost>`
                            <markdown-component
                                    :content=${x => x.post?.content}
                            ></markdown-component>
                        `)}
                        ${when(x => x.post?.contentType == ContentType.Plain, html<ViewPost>`
                            <span class="post-text">${x => x.post?.content}</span>
                        `)}
                        <div class="post-container3">
                            <span>${x => x.post?.author?.displayName} | ${x => new Date(x.post?.published || new Date()).toLocaleDateString()}</span>
                            <div class="like-post-icon" @click="${x => x.likePost()}"
                                 :innerHTML="${_ => icon({prefix: 'fas', iconName: "thumbs-up"}).html}"></div>
                            <div @click="${x => x.toggleLikesModal()}">
                                See Likes
                            </div>
                            ${when(x => x.viewLikes, html`
                                <fast-dialog modal="true">
                                    <likes-modal
                                            :postAuthorId="${x => x.post?.author.id}"
                                            :postId="${x => x.postId}"
                                            :parent="${x => x}"
                                    ></likes-modal>
                                </fast-dialog>
                            `)}
                            <div
                                    class="create-comment-icon"
                                    @click="${x => x.toggleCreateCommentModal()}"
                                    :innerHtml="${_ => icon({prefix: 'fas', iconName: "comment-dots"}).html}">
                                Post Comment
                            </div>
                            ${when(x => x.viewCreateCommentModal, html`
                                <fast-dialog modal="true">
                                    <comment-modal
                                            :parent="${x => x}"
                                    >
                                    </comment-modal>
                                </fast-dialog>
                            `)}
                        </div>
                    </div>
                </div>
                ${when(x => x.userId == x.profileId, html<ViewPost>`
                    <a class="edit-post-button" href="/edit-post/${x => x.userId}/${x => x.post?.id}">Edit Post</a>
                `)}


                ${when(x => x.commentsLoaded, html`
            <ul class="post-ul list">
                <li class="post-li list-item">
                    ${repeat(x => x.comments || [], html<Comment>`
                    <div class="comment-container">
                        <span class="comment-display-name">${x => x.author.display_name}</span>
                        <span class="comment-content">${x => x.comment}</span>
                        <img
                                alt="image"
                                src="https://play.teleporthq.io/static/svg/default-img.svg"
                                class="comment-profile-icon"
                        />
                    </div>
                `)}
                </li>
            </ul>
        `)}
            </div>
        `)}
        ${when(x => !x.post, html<ViewPost>`
            <h1>${x => x.loadedPostText}</h1>
        `)}
    </page-layout>
`;


