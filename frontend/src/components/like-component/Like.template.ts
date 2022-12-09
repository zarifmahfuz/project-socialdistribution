import { html, when } from "@microsoft/fast-element";
import { authorInfo } from "../author-info";
import { Like } from "./Like";

authorInfo;

export const LikeTemplate = html<Like>`
    <div class="like ${x => x.layoutStyleClass}">
        <author-info
            :authorId=${x => x.authorId}
            :author=${x => x.author}
        ></author-info>
        liked your <a href="${x => x.getPostUrl()}"><strong>${when(x => x.comment, html`comment on this `)}post!</strong></a>
    </div>
`;