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
  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    public fb: FormBuilder
  ) {
  }

  newLinkForm: FormGroup

  ngOnInit(): void {
    this.newLinkForm = this.fb.group({
      short_link: ['',[
        Validators.required,
        Validators.minLength(this.minUrlLength),
        Validators.maxLength(this.maxUrlLength)]],
      title: ['',[
        Validators.required,
        Validators.minLength(this.minTitleLength),
        Validators.maxLength(this.maxTitleLength)]
      ],
      long_link: ['', [
        Validators.required,
        Validators.pattern('^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+$')
      ]],
    });
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
      this.home()
    }, error => {
      console.log(error)
    })

  }
}
