import {Component, OnInit} from '@angular/core';
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {ApiService} from "../../services/api.service";
import {AuthService} from "../../services/auth.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent implements OnInit {
  constructor(
    private _api: ApiService,
    private _auth: AuthService,
    private router: Router,
    public fb: FormBuilder
  ) {
  }

  form: FormGroup
  disabled = false

  ngOnInit(): void {
    this.form = this.fb.group({
      email: ['', Validators.required],
      password: ['', Validators.required],
      username: ['', Validators.required]
    });
  }

  register() {
    let b = this.form.value

    this._api.postTypeRequest('register', b).subscribe((res: any) => {
      if (res.status_code == 200) {
        this._api.postTypeRequest('login', b).subscribe((res: any) => {
          if (res.access_token) {
            this._auth.setDataInLocalStorage('token', res.access_token)
            this.router.navigate(['home'])
          }
        }, err => {
          console.log(err)
        })
      }
    }, err => {
      console.log(err)
    });
  }

}
