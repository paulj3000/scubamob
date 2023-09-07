import React from "react";
import PropTypes from "prop-types";

export default class Dashboard extends React.Component {
  static propTypes = {
    value: PropTypes.string,
  };

  render() {
    return (
      <div className="component-display">
        <div>xxx -> {this.props.value} <- xxx</div>
      </div>
    );
  }
}
