const BasicsModal = (props) => {
  return (
    <div>
      <Dialog
        open={props.open}
        onClose={props.handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title"　className={classes.title}>Basics</DialogTitle>
        <DialogContent className={classes.content}>
            <div className={classes.text}> 
                <TextField id="standard-basic" label="name" fullWidth/>
                <TextField id="standard-basic" label="password" fullWidth/>
            </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={props.handleClose} className={classes.signUpButton}>
            Basics
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}
export default BasicsModal
