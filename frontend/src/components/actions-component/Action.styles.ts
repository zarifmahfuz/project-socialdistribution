import { accentFillRest, accentForegroundActive, accentForegroundRest, neutralFillStealthHover, neutralLayer2, typeRampPlus1FontSize, typeRampPlus2FontSize } from "@microsoft/fast-components";
import { css } from "@microsoft/fast-element";

export const ActionsStyles = css`
    follower-component {
        cursor: pointer;
    }

    follower-component:hover {
        background-color: lightgrey;
    }

    #share-modal, #comments-modal {
        position: fixed;
        z-index: 5;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto; 
        background-color: rgba(0, 0, 0, 0.4);
    }

    .modal-content {
        background-color: white;
        margin: 15% auto;
        padding: 20px;
        border-radius: 20px;
        width: 70%;
        background: linear-gradient(to bottom right, ${neutralLayer2}, ${accentFillRest});
    }

    .modal-content ul {
        max-height: 60vh;
        overflow: auto;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: ${typeRampPlus2FontSize};
        font-weight: bold;
    }

    .modal-header button, .make-comment {
        border-radius: 50px;
        padding: 8px 20px;
        border: 0;
        background-color: black;
        color: white;
        font-size: ${typeRampPlus1FontSize};
        cursor: pointer;
    }

    .make-comment {
        background-color: ${accentForegroundRest};
        font-size: ${typeRampPlus2FontSize};
    }

    .modal-open {
        display: block;
    }

    .modal-close {
        display: none;
    }

    .post-comment-area {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .post-comment-area textarea {
        width: 100%;
        height: 30vh;
        resize: none;
        margin: 16px 0;
    }

    .post-actions {
		display: flex;
		justify-content: space-around;
		align-items: center;
        margin: 8px 0;
	}

    .post-action-icon {
		width: 25px;
		height: 25px;
		cursor: pointer;
        color: #453d4e;
	}

    .share-post-area ul {
        margin: 0;
        padding: 0;
    }

    .comment-icon {
        width: 20px;
        height: 20px;
    }

	.liked {
		color: #14A9FF;
	}

	.post-action-icon:hover {
		color: ${accentForegroundActive};
	}


    button, input, optgroup, select, textarea {
        font-family: inherit;
        font-size: 100%;
        line-height: 1.15;
        margin: 0;
    }
`;
