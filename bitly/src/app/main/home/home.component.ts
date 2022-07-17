  import { Component, OnInit } from '@angular/core';
  import {AuthService} from "../../services/auth.service";
  import {ApiService} from "../../services/api.service";
  import {Subscription} from "rxjs";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {
  private linksSub: Subscription;
  links: []
  constructor(
    private _api : ApiService,
    private _auth: AuthService,
  ) { }

  ngOnInit(): void {
    this.home()
  }

  home(){
    this.linksSub = this._api.getTypeRequest('home').subscribe((res: any) => {
      this.links = res.links
      console.log(this.links)
      console.log(res)

    }, err => {
      console.log(err)
    });
  }
}
