var $ = require('jquery');
window.jQuery = $;
window.$ = $;

require('bootstrap-webpack');
require('font-awesome-webpack');
require('bootstrap-table');

require('../css/main.css');

var React = require('react/addons');
var ReactBootstrap = require('react-bootstrap');

var Navbar = ReactBootstrap.Navbar;
var Nav = ReactBootstrap.Nav;
var NavDropdown = ReactBootstrap.NavDropdown;
var NavItem = ReactBootstrap.NavItem;
var MenuItem = ReactBootstrap.MenuItem;
var Grid = ReactBootstrap.Grid;
var Row = ReactBootstrap.Row;
var Col = ReactBootstrap.Col;
var Table = ReactBootstrap.Table;
var Panel = ReactBootstrap.Panel;
var Modal = ReactBootstrap.Modal;
var Button = ReactBootstrap.Button;


var MetricsGroupView = React.createClass({
    render: function() {
        var rows = this.props.metrics.map(function(metric, i) {
            return (
                <tr>
                    <td>{metric.reps}RM</td>
                    <td>{metric.weight}</td>
                </tr>
            );
        });
        return (
            <Col xs={4}>
                <Panel header="Squat">
                    <Table fill condensed>
                        <tbody>
                            {rows}
                        </tbody>
                    </Table>
                </Panel>
            </Col>
        );
    }
});


var SelectExerciseView = React.createClass({
    render: function() {
        return (
            <div>xxx</div>
        );
    }
});


var AddExerciseMetricsModal = React.createClass({
    getInitialState: function() {
        return {exercises: []}
    },
    componentDidMount: function() {
        $.ajax({
            type: "GET",
            url: "/api/exercise",
            dataType: "json",
            success: function(data) {
                this.setState({exercises: data})
            }.bind(this)
        });
    },
    add: function() {
        this.props.add(this.state.selectedExercise);
    },
    render: function() {
        var exercises = (
            <p className="text-center">
                <br/><br/>
                <i className="fa fa-spinner fa-pulse fa-2x"></i>
            </p>
        );
        if (this.state.exercises != [])
            exercises = this.state.exercises.map(function(exercise) {
                return exercise.name;
            });
        return (
            <Modal show={this.props.showModal} onHide={this.props.onHide}>
              <Modal.Header closeButton>
                <Modal.Title>Add exercise</Modal.Title>
              </Modal.Header>
              <Modal.Body>
              {exercises}
              </Modal.Body>
              <Modal.Footer>
                <Button onClick={this.add} bsStyle='primary'>Add</Button>
              </Modal.Footer>
            </Modal>
        );
    }
});


var MetricsView = React.createClass({
    getInitialState: function() {
        return {metrics: [], showModal: false}
    },
    componentDidMount: function() {
        $.ajax({
            type: "GET",
            url: "/api/metric",
            dataType: "json",
            success: function(data) {
                this.setState({metrics: data})
            }.bind(this)
        });
    },
    showAddExerciseModal: function() {
        this.setState({showModal: true});
    },
    onHide: function() {
        this.setState({showModal: false});
    },
    addExercise: function(exercise) {
        var metrics = this.state.metrics;
        metrics.push({exercise: exercise, metrics: []});
        this.setState({metrics: metrics});
        this.setState({showModal: false});
    },
    render: function() {
        console.log(this.state.metrics)
        var views = this.state.metrics.map(function(metricsGroup, i) {
            return (<MetricsGroupView key={i} metrics={metricsGroup.metrics}/>);
        });
        return (
            <Grid style={{marginTop: "15px"}}>
                <Row>
                    <Col xs={12}>
                        <h1>Metrics</h1>
                        <div><a href='#' onClick={this.showAddExerciseModal}>Add exercise</a></div>
                        <AddExerciseMetricsModal showModal={this.state.showModal} onHide={this.onHide} add={this.addExercise}/>
                    </Col>
                </Row>
                <Row>
                    {views}
                </Row>
            </Grid>
        );
    }
});


var MainNav = React.createClass({
    selectView: function(view) {
        this.props.selectView(view)
    },
    render: function() {
        return (
          <Navbar brand='flexo' inverse fixedTop toggleNavKey={0}>
            <Nav right eventKey={0}>
                <NavItem eventKey={2} onSelect={this.selectView.bind(this, ProgramView)}>Program</NavItem>
                <NavItem eventKey={3} onSelect={this.selectView.bind(this, MetricsView)}>Metrics</NavItem>
                <NavDropdown eventKey={3} title={this.props.username} id='collapsible-navbar-dropdown'>
                    <MenuItem eventKey='1'>Profile</MenuItem>
                    <MenuItem eventKey='2'>Settings</MenuItem>
                    <MenuItem divider />
                    <MenuItem eventKey='4' onSelect={this.props.logout}>Logout</MenuItem>
                </NavDropdown>
            </Nav>
          </Navbar>
        );
    }
});


var ProgramView = React.createClass({
    render: function() {
        return (
            <Grid style={{marginTop: "15px"}}>
                <Row>
                    <Col xs={12}><h1>Program</h1></Col>
                </Row>
            </Grid>
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
        return {loggedIn: null, username: null, view: (<ProgramView/>)};
    },
    componentDidMount: function() {
        $.ajax({
            type: "GET",
            url: "/api/login",
            dataType: "json",
            success: function(data) {
                this.setState({loggedIn: data.ok, username: data.name})
            }.bind(this)
        });
    },
    logout: function() {
        this.setState({loggedIn: null});
        $.ajax({
            type: "GET",
            url: "/api/logout",
            success: function(data) {
                this.setState({loggedIn: false});
            }.bind(this)
        });
    },
    login: function(d) {
        this.setState({loggedIn: null});
        $.ajax({
            type: "POST",
            url: "/api/login",
            data: JSON.stringify(d),
            contentType: "application/json",
            dataType: "json",
            success: function(data) {
                this.setState({loggedIn: data.ok, username: data.name})
            }.bind(this),
            failure: function(errMsg) {
                console.log(errMsg);
            }
        });
    },
    selectView: function(view) {
        this.setState({view: React.createFactory(view)()});
    },
    render: function() {
        var content = '';
        if (this.state.loggedIn)
              content = (
                <div>
                    <MainNav logout={this.logout} username={this.state.username} selectView={this.selectView}/>
                    {this.state.view}
                </div>
            );
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