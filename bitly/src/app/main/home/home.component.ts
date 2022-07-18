import {Component, OnInit} from '@angular/core';
import {AuthService} from "../../services/auth.service";
import {ApiService} from "../../services/api.service";
import {Subscription} from "rxjs";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  private linksSub: Subscription;
  links: []
  username = ""
  minUrlLength: number = 3
  maxUrlLength: number = 60
  minTitleLength: number = 3
  maxTitleLength: number = 60
  maxTagLength: number = 12

  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    public fb: FormBuilder
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
        Validators.pattern('^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+$')
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
      this.username = res.username
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
    let b = this.newLinkForm.value
    let short_link = b['short_link']
    this._api.postTypeRequest('url/' + short_link, b).subscribe((res: any) => {
      this.newTagForm.reset()
      this.home()
    }, error => {
      console.log(error)
    })

  }

  newTagLink(short_link: string){
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
}
