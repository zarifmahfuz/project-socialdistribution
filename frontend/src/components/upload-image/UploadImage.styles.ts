import { css } from "@microsoft/fast-element";

export const UploadImageStyles = css`
:host {
    width: 80%;
    margin: 5rem 0;
}

.image-form {
	background-color: white;
    padding: 16px;
    display: flex;
    border-radius: var(--dl-radius-radius-radius8);
    flex-direction: column;
    align-items: center;
  }

  .image-form button {
	align-self: center;
    margin-top: var(--dl-space-space-unit);
    border-width: 0px;
    border-radius: var(--dl-radius-radius-radius8);
    background-color: #b4cde6;
  }

  .image-form img{
    max-width: 50%;
    object-fit: cover;
    object-position: 50%;
    background-color: lightgrey;
    border: solid lightgrey 3px;
  }

  .image-form strong {
	margin: 16px 0;
  }

  .create-image-upload {
	background-color: lightgrey;
	border-radius: 16px;
	padding: 8px;
  }

  .create-image-button {
    color: var(--dl-color-gray-black);
    display: inline-block;
    padding: 0.5rem 1rem;
    border-color: var(--dl-color-gray-black);
    border-width: 1px;.
    border-radius: 4px;
    background-color: var(--dl-color-gray-white);
    color: rgb(39, 123, 192);
    font-weight: bold;
    cursor: pointer;
  }

  button, input {
    font-family: inherit;
    font-size: 100%;
    line-height: 1.15;
    margin: 0;
  }

  h2, p {
    margin: 6px 0;
  }
`;