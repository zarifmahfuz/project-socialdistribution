import { html, when } from "@microsoft/fast-element";
import { AuthorInfo } from "./AuthorInfo";

export const AuthorInfoTemplate = html<AuthorInfo>`
    <h4>
        ${when(x => x.author?.profileImage !== "", html<AuthorInfo>`
            <img class="profile-image" src="${x => x.author?.profileImage}">
        `)}
        <a href="${x => x.getAuthorUrl(x.authorId)}">${x => x.author?.displayName + " "}</a>
        ${when(x => x.published, html<AuthorInfo>`
            <small>${x => " | " + x.published?.toLocaleString()}</small>
        `)}
    </h4>
`;