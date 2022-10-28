import { library } from "@fortawesome/fontawesome-svg-core";
import { faPencil } from "@fortawesome/free-solid-svg-icons";
import { observable } from "@microsoft/fast-element";
import { SocialApi } from "../../libs/api-service/SocialApi";
import { PaginatedResponse, Post } from "../../libs/api-service/SocialApiModel";
import { SocialApiTransform } from "../../libs/api-service/SocialApiTransform";
import { FeedType } from "../../libs/core/PageModel";
import { Page } from "../Page";

const PAGE_SIZE = 10;

export class Home extends Page {
    @observable
    public visibilePosts: Post[] = [];

    public loadMore?: HTMLElement;

    private observer?: IntersectionObserver;

    @observable
    public paginatedResponse?: PaginatedResponse | null;

    @observable
    public feedType: FeedType = FeedType.All;

    constructor() {
        super();

        this.addIcons();

        this.observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.getPosts();
                }
            })
        })

        this.getPosts();
    }

    public async changeFeed(feedType: FeedType) {
        this.feedType = feedType;
        this.visibilePosts.splice(0, this.visibilePosts.length);
        this.paginatedResponse = null;
        this.observer?.disconnect();
        await this.getPosts();
    }

    public getFeedTypeStyles(feedType: FeedType) {
        if (this.feedType == feedType) {
            return "tab-active";
        }
        return "";
    }

    private addIcons() {
        library.add(faPencil);
    }

    private async getPosts() {
        try {
            let responseData: PaginatedResponse | null;

            if (this.paginatedResponse?.next) {
                responseData = await SocialApi.fetchPaginatedNext(this.paginatedResponse.next);
                console.log(responseData)
                if (responseData) {
                    this.paginatedResponse = responseData;
                    this.setVisiblePosts()
                }
            } else if (!this.paginatedResponse) {
                responseData = await this.getPostsFromFeedType();
                console.log(responseData)
                if (responseData) {
                    this.paginatedResponse = responseData;
                    this.setVisiblePosts()
                    if (this.loadMore) {
                        this.observer?.observe(this.loadMore);
                    }
                }
            } else {
                responseData = this.paginatedResponse || null;
            }
        } catch (e) {
            console.error("Public post fetch failed", e);
        }
    }

    private async getPostsFromFeedType(): Promise<PaginatedResponse | null> {
        switch (this.feedType) {
            case FeedType.All:
                return await SocialApi.fetchPaginatedPublicPosts(1, PAGE_SIZE);
            case FeedType.Stream: {
                if (!this.user?.id) {
                    return null;
                }
                return await SocialApi.fetchPaginatedInbox(this.user?.id, 1, PAGE_SIZE);
            }
        }
    }

    private setVisiblePosts() {
        if (!this.paginatedResponse?.results) {
            return;
        }

        for (var postData of this.paginatedResponse?.results) {
            if (!postData.type || postData.type == "post") {
                const post = SocialApiTransform.postDataTransform(postData);
                if (post) {
                    this.visibilePosts.push(post);
                }
            }
        }
    }
}