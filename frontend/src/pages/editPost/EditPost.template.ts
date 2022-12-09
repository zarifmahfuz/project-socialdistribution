import { html, ref, when } from "@microsoft/fast-element";
import { layoutComponent } from "../../components/base-layout";
import { LayoutHelpers } from "../../libs/core/Helpers";
import { EditPost } from "./EditPost";

layoutComponent;

export const EditPostPageTemplate = html<EditPost>`
  <page-layout
    :userId="${x => x.userId}"
    :user="${x => x.user}"
    :layoutType="${x => x.layoutType}"
    :layoutStyleClass="${x => LayoutHelpers.getLayoutStyle(x.layoutType)}">
    ${when(x => x.post, html<EditPost>`
    <div class="edit-post-container">
        <div class="edit-post-banner">
            <h1 class="edit-post-text">Edit A Post</h1>
        </div>
        <form ${ref("form")} @submit="${(x, c) => x.editPost(c.event)}" class="edit-post-container1">
            <input
                    type="text"
                    required=""
                    autofocus=""
                    placeholder="Title"
                    class="edit-post-textinput input"
                    value="${x => x.post?.title}"
                    name="title"
            />
            <textarea
              placeholder="Description"
              class="edit-post-textarea textarea"
              name="description"
              maxlength="280"
            >${x => x.post?.description}</textarea>
            <textarea
                    placeholder="Content"
                    class="edit-post-textarea textarea"
                    name="content"
            >${x => x.post?.content}</textarea>
            <button class="edit-post-button button" type="button">
            <span class="edit-post-text01">
              <span class="edit-post-text02">Upload Image</span>
              <br/>
            </span>
            </button>
            <div class="edit-post-container2">
                <span class="edit-post-text04">Visibility:</span>
                <select class="edit-post-select">
                    <option value="Public" name="visibility" selected="${x => {
    if (x.post?.visibility === "PUBLIC") return "selected"
  }}">Public
                                                          </option>
                                                          <option value="Private" selected="${x => {
    if (x.post?.visibility === "PRIVATE") return "selected"
  }}">Private
                                                          </option>
                                                          <option value="Friends Only" selected="${x => {
    if (x.post?.visibility === "FRIENDS") return "selected"
  }}">Friends Only
                    </option>
                </select>
            </div>
            <div class="edit-post-container3">
                <button class="edit-post-button1 button" type="button" @click="${x => x.deletePost()}">
              <span class="edit-post-text05">
                <span class="edit-post-text06">Delete</span>
                <br/>
              </span>
                </button>
                <button class="edit-post-button2 button" type="submit">
              <span class="edit-post-text08">
                <span class="edit-post-text09">Done</span>
                <br/>
              </span>
                </button>
            </div>
        </form>
    </div>
    `)}
    ${when(x => !x.post, html<EditPost>`
      <h1>${x => x.loadedPostText}</h1>
    `)}
  </page-layout>
`;
