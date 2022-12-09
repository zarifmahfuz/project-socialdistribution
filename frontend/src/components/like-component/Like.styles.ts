import { accentForegroundRest, neutralFillStealthHover } from "@microsoft/fast-components";
import { css } from "@microsoft/fast-element";
import { LayoutStyleClass } from "../../libs/core/PageModel";

export const LikeStyles = css`
    .like {
        background-color: ${neutralFillStealthHover};
        border-radius: 20px;
        margin: 8px 0px;
        padding: 8px;
        display: flex;
        align-items: center;
        flex-direction: column;
    }

    .like.${LayoutStyleClass.Desktop} {
        justify-content: flex-start;
        align-items: center;
        flex-direction: row;
    }

    a, a:hover, a:visited, a:active {
        text-decoration: none;
        color: ${accentForegroundRest};
        padding-left: 4px;
    }
`;
