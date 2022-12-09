import { html, when } from "@microsoft/fast-element";
import { actionsComponent } from "../actions-component";
import { authorInfo } from "../author-info";
import { Comment } from "./Comment";

authorInfo;
actionsComponent;

export const CommentTemplate = html<Comment>`
    <li class="comment-container">
        <author-info
            :authorId=${x => x.authorId}
            :author=${x => x.author}
            :published=${x => x.published}
        ></author-info>
        <span class="comment-content">${x => x.comment}</span>
        <actions-component
            :commentId=${x => x.commentId}
            :userId=${x => x.userId}
            :profileId=${x => x.authorId}
            :user=${x => x.user}
        ></actions-component>
        ${when(x => x.inbox, html<Comment>`
            <a class="link-to-post" href="${x => x.getPostUrl()}"><strong>Go To Post</strong></a>
        `)}
    </li>
`;