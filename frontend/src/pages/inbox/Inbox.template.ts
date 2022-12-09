import { html, ref, repeat, when } from "@microsoft/fast-element";
import { commentComponent } from "../../components/comment-component";
import { feedPost } from "../../components/feed-post";
import { followerComponent } from "../../components/follower-component";
import { likeComponent } from "../../components/like-component";
import { ContentType, FollowRequest, Post, Comment, Like } from "../../libs/api-service/SocialApiModel";
import { LayoutHelpers } from "../../libs/core/Helpers";
import { Inbox } from "./Inbox";

feedPost;
followerComponent;
commentComponent;
likeComponent;

export const InboxPageTemplate = html<Inbox>`
    <page-layout
        :userId="${x => x.userId}"
        :user="${x => x.user}"
        :layoutType="${x => x.layoutType}"
        :layoutStyleClass="${x => LayoutHelpers.getLayoutStyle(x.layoutType)}">
        <h1>Inbox</h1>
        <div class="inbox-container">
            ${repeat(x => x.inbox, html`
                ${when(x => x instanceof Post && x.contentType != ContentType.Image, html<Post>`
                    <feed-post
                        :post=${x => x}>
                    </feed-post>
                `)}
                ${when(x => x instanceof FollowRequest, html<FollowRequest>`
                    <follower-component
                        :profile=${x => x.sender}
                        :user=${(_, c) => c.parent.user}
                        :request=${_ => true}
                        :layoutStyleClass=${(x, c) => LayoutHelpers.getLayoutStyle(c.parent.layoutType)}>
                    </follower-component>
                `)}
                ${when(x => x instanceof Comment, html<Comment>`
                    <comment-component
                        :comment=${x => x.comment}
                        :author=${x => x.author}
                        :authorId=${x => x.author?.id}
                        :published=${x => x.published}
                        :commentId=${x => x.id}
                        :user=${(x, c) => c.parent.user}
                        :userId=${(x, c) => c.parent.userId}
                        :inbox=${_ => true}>
                    </comment-component>
                `)}
                ${when(x => x instanceof Like, html<Like>`
                    <like-component
                        :author=${x => x.author}
                        :authorId=${x => x.author?.id}
                        :post=${x => x.post}
                        :comment=${x => x.comment}
                        :userId=${(x, c) => c.parent.userId}
                        :layoutStyleClass=${(x, c) => LayoutHelpers.getLayoutStyle(c.parent.layoutType)}>
                    </like-component>
                `)}
            `)}
            <div ${ref("loadMore")} class="loading"></div>
        </div>
    </page-layout>
`;