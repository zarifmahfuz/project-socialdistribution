import { accentForegroundRest, neutralFillStealthHover, neutralLayer2 } from "@microsoft/fast-components";
import { css } from "@microsoft/fast-element";

export const CommentStyles = css`
    .comment-container {
        display: flex;
        flex-direction: column;
        padding: 16px;
        border-radius: 20px;
        background-color: ${neutralFillStealthHover};
        margin: 8px 0;
    }

    .comments-box {
        width: 90%
    }

    .link-to-post {
        background-color: ${neutralLayer2};
        padding: 8px;
        border-radius: 20px;
        margin: 8px 0;
        width: fit-content;
    }

    a, a:hover, a:visited, a:active {
        text-decoration: none;
        color: ${accentForegroundRest};
    }
`;
