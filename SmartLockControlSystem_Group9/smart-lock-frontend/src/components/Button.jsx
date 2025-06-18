import React from 'react';
import PropTypes from 'prop-types';

const Button = ({ 
  onClick, 
  text, 
  variant = 'primary', 
  className = '', 
  disabled = false 
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`button button-${variant} ${className}`}
      type="button"
    >
      {text}
    </button>
  );
};

Button.propTypes = {
  onClick: PropTypes.func.isRequired,
  text: PropTypes.string.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary']),
  className: PropTypes.string,
  disabled: PropTypes.bool
};

export default Button;