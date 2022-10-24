import React from 'react';
import ReactDOM from 'react-dom';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import CircularProgress from '@mui/material/CircularProgress';
import Backdrop from '@mui/material/Backdrop';
import Paper from '@mui/material/Paper'
import ListItemAvatar from '@mui/material/ListItemAvatar';
import Avatar from '@mui/material/Avatar';
import './index.css';


const API_URL_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : ''

class Example extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            query: '',
            result: [],
            loading: false,
        }
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event, value) {
        event.preventDefault();
        const timer = setTimeout(() => this.setState({ loading: true }), 250);
        this.setState({ query: value });
        fetch(API_URL_BASE + '/search', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({query: value})
        })
            .then(res => res.json())
            .then(
                (res) => {
                    this.setState({
                        result: res,
                        loading: false,
                    });
                },
                (err) => {
                    this.setState({
                        loading: false,
                        result: [],
                    });
                }
            ).finally(() => {
                clearTimeout(timer);
            });
    }

    render() {
        return (
            <div>
                <Paper style={{ position: "sticky", top: 0, zIndex: 1, padding: 12 }}>
                    <QueryForm value={this.state.query} disabled={this.state.loading} handleSubmit={this.handleSubmit} handleChange={this.handleChange} />
                    {this.state.query && (<p>You searched for '{this.state.query}'</p>)}
                </Paper>
                <Sentence values={this.state.result} disabled={this.state.loading} />
                <Backdrop
                    sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
                    open={this.state.loading}
                >
                    <CircularProgress color="inherit" size="100px" />
                </Backdrop>
            </div>
        );
    }
}

function SentenceListItem(props) {
    const getColor = (value) => {
        var hue = ((value) * 120).toString(10);
        return ["hsl(", hue, ",100%,50%)"].join("");
    }
    return (
        <ListItem >
            <ListItemAvatar>
                <Avatar sx={{ color: 'black', backgroundColor: getColor(props.value.score), fontSize: 16 }}>{props.value.score.toFixed(2)}</Avatar>
            </ListItemAvatar>
            <ListItemText primary={props.value.title} secondary={props.value.text} style={{textAlign: "justify"}}></ListItemText>
        </ListItem>
    );
}


function Sentence(props) {
    return (
        <List dense>
            {props.values.map((v) => <SentenceListItem key={v.id} value={v} />)}
        </List>
    );
}

class QueryForm extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            value: ''
        }
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(event) {
        this.setState({ value: event.target.value });
    }

    render() {
        return (
            <form onSubmit={(e) => this.props.handleSubmit(e, this.state.value)}>
                <Stack direction="row" alignItems="center" justifyContent="center" spacing={1}>
                    <TextField disabled={this.props.disabled} fullWidth label="Query" value={this.state.value} onChange={this.handleChange}>
                    </TextField>
                    <Button disabled={this.props.disabled || !this.state.value || this.state.value === this.props.value} variant="contained" type="submit" size="large">Search</Button>
                </Stack>
            </form>
        );
    }
}

ReactDOM.render(
    <Example />,
    document.getElementById('root')
);
