import {Component, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth.service";
import {ApiService} from "../../services/api.service";
import {Subscription} from "rxjs";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {Router} from "@angular/router";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  private linksSub: Subscription;
  links: any[] = []
  search_result: any[] = []
  search_bar_result: any[] = []
  private userTagsSub: Subscription;
  userTags: any[] = []
  tags_search: any = []
  tags_search_result: any[] = []
  username = ""
  minUrlLength: number = 3
  maxUrlLength: number = 60
  minTitleLength: number = 3
  maxTitleLength: number = 60
  maxTagLength: number = 12
  disabled = false

  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    public fb: FormBuilder,
    private router: Router
  ) {
  }

  newLinkForm: FormGroup
  newTagForm: FormGroup

  ngOnInit(): void {
    this.newLinkForm = this.fb.group({
      short_link: ['', [
        Validators.required,
        Validators.minLength(this.minUrlLength),
        Validators.maxLength(this.maxUrlLength)]],
      title: ['', [
        Validators.required,
        Validators.minLength(this.minTitleLength),
        Validators.maxLength(this.maxTitleLength)]
      ],
      long_link: ['', [
        Validators.required,
        Validators.pattern(/^[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/)
      ]],
    });

    this.newTagForm = this.fb.group({
      tag_name: ['', [
        Validators.required,
        Validators.maxLength(this.maxTagLength)
      ]],
      short_link: [''],
    })

    this.home()
  }

  home() {
    this.linksSub = this._api.getTypeRequest('home').subscribe((res: any) => {
      this.links = res.links
      this.search_result = res.links
      this.search_bar_result = res.links
      this.tags_search_result = res.links
      this.username = res.username
      this.userTags = res.userTags
    }, err => {
      console.log(err)
    });
  }

  deleteLink(short_url: string) {
    this._api.deleteTypeRequest('' + short_url).subscribe((res: any) => {
        this.home()
      }, error => {
        console.log(error)
      }
    )
  }

  newLinkSubmit() {
    this.disabled = true;
    if (!this.newLinkForm.valid) {
      this.newLinkForm.markAllAsTouched();
      this.disabled = false;
      return;
    }
    let b = this.newLinkForm.value
    let short_link = b['short_link']
    this._api.postTypeRequest('url/' + short_link, b).subscribe((res: any) => {
      this.newLinkForm.reset()
      this.home()
      this.disabled = false;
    }, error => {
      console.log(error)
    })

  }

  newTagLink(short_link: string) {
    this.newTagForm.patchValue({short_link: short_link})
    let b = this.newTagForm.value
    let tag_name = b['tag_name']
    this._api.postTypeRequest('url/' + short_link + '/tags/' + tag_name, b).subscribe((res: any) => {
      this.newTagForm.reset()
      this.home()
    }, error => {
      console.log(error)
    })
  }

  onSearchEnter(e: KeyboardEvent, query: string) {
    this.onSearch(query);
  }


  onSearch(query: string) {
    this.search_bar_result = this.links.filter((obj) => {
      return obj[2].toLowerCase().includes(query.toLowerCase());
    });

    this.search_result = this.links.filter(value => this.tags_search_result.includes(value));
    this.search_result = this.search_result.filter(value => this.search_bar_result.includes(value));

  }

  updateTagsSearch(tag: string) {

    const index = this.tags_search.indexOf(tag);
    if (index == -1) {
      this.tags_search.push(tag);
    } else {
      this.tags_search.splice(index, 1);
    }

    this.tags_search_result = this.links.filter((obj) => {
      return this.tags_search.every((t: string) => {
        return obj[5].includes(t)
      })
    })

    console.log(this.tags_search)

    this.search_result = this.links.filter(value => this.tags_search_result.includes(value));
    this.search_result = this.search_result.filter(value => this.search_bar_result.includes(value));
  }


  remove_tag(short_link: string, tag: string){


    this._api.deleteTypeRequest('url/' + short_link + '/tags/' + tag).subscribe((res: any) => {
      this.home()
    }, error => {
      console.log(error)
    })
  }


  logout(){
    localStorage.removeItem('token');
    this._auth.clearStorage()

    this.router.navigate(['login']);

  }

}


