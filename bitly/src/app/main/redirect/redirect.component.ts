import {Component, Inject, Input, OnInit} from '@angular/core';
import {ApiService} from "../../services/api.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-redirect',
  templateUrl: './redirect.component.html',
  styleUrls: ['./redirect.component.css']
})
export class RedirectComponent implements OnInit {

  long_url: string = ""
  href = ""

  constructor(
    private _api: ApiService,
    private router: Router,
  ) {
  }

  ngOnInit(): void {
    this.href = this.router.url;
    this.href = this.href.substring(1);
    this.redirect(this.href)
  }

  redirect(url: string) {
    return this._api.getTypeRequest(url).subscribe((res: any) => {
      this.long_url = res.link
      console.log(this.long_url)
      window.location.href = 'http://' + this.long_url
    }, error => {
      console.log(error)
    })
  }
}
