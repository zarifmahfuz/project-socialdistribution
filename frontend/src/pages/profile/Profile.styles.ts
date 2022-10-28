import { accentColor, accentFillRest, accentForegroundActive, neutralColor, typeRampPlus1FontSize, typeRampPlus1LineHeight, typeRampPlus2FontSize } from "@microsoft/fast-components";
import { css } from "@microsoft/fast-element";
import { LayoutStyleClass } from "../../libs/core/PageModel";

export const ProfilePageStyles = css`
    .profile-background {
        height: 20vh;
        width: 56.25%;
        position: absolute;
        margin-top: -24px;
        background: linear-gradient(to bottom right, ${neutralColor}, ${accentColor});
        z-index: 0;
        border-radius: 20px 0 0 0;
    }

    .profile-background.${LayoutStyleClass.Mobile} {
        width: 100%;
        border-radius: 0;
    }

    .profile-info {
        z-index: 1;
        padding-top: 7.5vh;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        align-content: center;
    }
    
    .profile-image {
        width: 150px;
        height: 150px;
        background-color: lightgrey;
    }

    .display-name {
        display: flex;
        width: 90%;
        justify-content: space-between;
        align-items: center;
    }

    .display-name button, .user-buttons a {
        border-radius: 50px;
        font-size: ${typeRampPlus1FontSize};
        padding: 0 16px;
        height: 5vh;
        background-color: ${accentForegroundActive};
        color: white;
        border: 0;
        font-weight: bold;

        display: flex;
        place-content: center;
        align-items: center;
        cursor: pointer;
    }

    .display-name button.true {
        background-color: ${accentForegroundActive};
        color: white;
    }

    .display-name button.false {
        background-color: white;
        border: 2px solid lightgrey;
        color: black;
    }

    .user-buttons {
        display: flex;
        width: 90%;
        justify-content: space-between;
        align-items: center;
    }

    .followers {
        margin-left: auto;
    }

    #edit-profile {
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
    }

    .edit-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: ${typeRampPlus2FontSize};
        font-weight: bold;
    }

    .edit-header button {
        border-radius: 50px;
        padding: 8px 20px;
        border: 0;
        background-color: black;
        color: white;
        font-size: ${typeRampPlus1FontSize};
        cursor: pointer;
    }

    fast-text-field {
        width: 100%;
        margin-bottom: 12px;
    }

    .form-element {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-content: center;
        align-items: center;
    }

    .modal-open {
        display: block;
    }

    .modal-close {
        display: none;
    }

    a, a:hover, a:visited, a:active {
        text-decoration: none;
    }
`;