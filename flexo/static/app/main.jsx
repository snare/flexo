var $ = require('jquery');
window.jQuery = $;
window.$ = $;

require('bootstrap-webpack');
require('font-awesome-webpack');

require('../css/main.css');

var React = require('react/addons');
var ReactBootstrap = require('react-bootstrap');

var Navbar = ReactBootstrap.Navbar;
var Nav = ReactBootstrap.Nav;
var NavDropdown = ReactBootstrap.NavDropdown;
var NavItem = ReactBootstrap.NavItem;
var MenuItem = ReactBootstrap.MenuItem;


var MainNav = React.createClass({
    render: function() {
        return (
          <Navbar brand='flexo' inverse fixedTop toggleNavKey={0}>
            <Nav right eventKey={0}>
              <NavItem eventKey={1} href='#'>Link</NavItem>
              <NavItem eventKey={2} href='#'>Link</NavItem>
              <NavDropdown eventKey={3} title='Dropdown' id='collapsible-navbar-dropdown'>
                <MenuItem eventKey='1'>Action</MenuItem>
                <MenuItem eventKey='2'>Another action</MenuItem>
                <MenuItem eventKey='3'>Something else here</MenuItem>
                <MenuItem divider />
                <MenuItem eventKey='4'>Separated link</MenuItem>
              </NavDropdown>
              <NavItem eventKey={4} href='#' onClick={this.props.logout}>Logout</NavItem>
            </Nav>
          </Navbar>
        );
    }
});


var DashboardView = React.createClass({
    render: function() {
        return (
          <div>
            <MainNav logout={this.props.logout}/>
          </div>
        );
    }
});


var LoginView = React.createClass({
    mixins: [React.addons.LinkedStateMixin],
    getInitialState: function() {
        return {name: '', password: ''};
    },
    login: function() {
        this.props.login(this.state);
    },
    render: function() {
        return (
            <div className="container">
              <form className="form-signin">
                <h2 className="form-signin-heading">Flexo</h2>
                <label for="inputEmail" className="sr-only">Email address</label>
                <input type="email" id="inputEmail" className="form-control" placeholder="Username" required="" autofocus="" valueLink={this.linkState('name')} />
                <label for="inputPassword" className="sr-only">Password</label>
                <input type="password" id="inputPassword" className="form-control" placeholder="Password" required="" valueLink={this.linkState('password')} />
                <div className="checkbox">
                  <label>
                    <input type="checkbox" value="remember-me"/> Remember me
                  </label>
                </div>
                <button className="btn btn-lg btn-primary btn-block" onClick={this.login}>Sign in</button>
              </form>
            </div>
        );
    }
});


var LoadingView = React.createClass({
    render: function() {
        return (
            <p className="text-center">
                <br/><br/><br/>
                <i className="fa fa-spinner fa-pulse fa-3x"></i>
            </p>
        );
    }
});


var MainView = React.createClass({
    getInitialState: function() {
        return {loggedIn: null};
    },
    componentDidMount: function() {
        $.ajax({
            type: "GET",
            url: "/login",
            dataType: "json",
            success: function(data) {
                this.setState({loggedIn: data.ok})
            }.bind(this)
        });
    },
    logout: function() {
        this.setState({loggedIn: null});
        $.ajax({
            type: "GET",
            url: "/logout",
            success: function(data) {
                this.setState({loggedIn: false});
            }.bind(this)
        });
    },
    login: function(d) {
        this.setState({loggedIn: null});
        $.ajax({
            type: "POST",
            url: "/login",
            data: JSON.stringify(d),
            contentType: "application/json",
            dataType: "json",
            success: function(data) {
                this.setState({loggedIn: data.ok})
            }.bind(this),
            failure: function(errMsg) {
                console.log(errMsg);
            }
        });
    },
    render: function() {
        var content = '';
        if (this.state.loggedIn)
            content = (<DashboardView logout={this.logout}/>);
        else if (this.state.loggedIn == null)
            content = (<LoadingView/>);
        else
            content = (<LoginView login={this.login}/>);
        return content;
    }
});


React.render(
    <MainView/>,
    document.getElementById('main')
);