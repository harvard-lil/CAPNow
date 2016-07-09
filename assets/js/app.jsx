var React = require('react');
var Dropzone = require('react-dropzone');
var request = require('superagent');

require('superagent-django-csrf');

var VolumeBox = React.createClass({
  loadVolumesFromServer: function() {
    request.get(this.props.url).end((err, res)=>{
      if(err){
        console.error(this.props.url, err.toString());
      }else{
        this.loadInterval && this.setState({data: res.body});
      }
    });
  },
  updateStateData: (data) => {
    this.setState({data: data})
  },
  handleCaseSubmit: function(caseData) {
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadVolumesFromServer();
    this.loadInterval = setInterval(this.loadVolumesFromServer, this.props.pollInterval);
  },
  componentWillUnmount () {
      this.loadInterval && clearInterval(this.loadInterval);
      this.loadInterval = false;
  },
  render: function() {
    return (
      <div className="volumeBox">
        <CaseForm updateStateData={this.updateStateData}/>

        <VolumeList data={this.state.data} />
      </div>
    );
  }
});

var VolumeList = React.createClass({
  render: function() {
    var volumeNodes = this.props.data.map(function(volume) {
      return (
        <Volume key={volume.id} data={volume}/>
      );
    });
    return (
      <div className="volumeList">

        <div className="row">
          <div className="col-lg-12">
            <h2>Volumes</h2>
          </div>
        </div>

        {volumeNodes}
      </div>
    );
  }
});

var Volume = React.createClass({
  render: function() {
    var caseNodes = this.props.data.cases.map(function(caseData) {
      return (
        <Case key={caseData.id} data={caseData}/>
      );
    });
    return (
      <div className="volume">
        <div className="row">
          <div className="col-lg-12">
            <h4>{this.props.data.volume_number} {this.props.data.series}</h4>

            {caseNodes}
          </div>
        </div>
      </div>
    );
  }
});

var Case = React.createClass({
  render: function() {
    return (
      <div className="case">
        <div className="row">
          <div className="col-lg-12"><h5>{this.props.data.citation}</h5></div>
        </div>
        <div className="row">
          <div className="col-lg-2"><a href={this.props.data.manuscript}>download manuscript</a></div>
          <div className="col-lg-2"><a href={this.props.data.proof.docx}>download proof .docx</a></div>
          <div className="col-lg-2"><a href={this.props.data.proof.pdf}>download proof .pdf</a></div>
        </div>
      </div>
    );
  }
});

var CaseForm = React.createClass({
  getInitialState: function () {
    return {
      files: []
    };
  },

  onDrop: function(files){
    var req = request.post(createCaseURL);
    files.forEach((file)=> {
      req.attach("manuscript", file);
    });
    req.end((err, res)=>{
      if(err){
        console.log("Error submitting case: ", err)
      }
    });
  },

  render: function () {
    return (
      <div className="caseForm">

        <div className="row">
          <div className="col-lg-12">
            <Dropzone
              ref="dropzone"
              onDrop={this.onDrop}
              multiple={false}
              accept="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              disablePreview={true}
              style={{
                width: "100%",
                borderWidth: 2,
                borderColor: '#666',
                borderStyle: 'dashed',
                borderRadius: 5,
                padding: "1em"
              }}
              activeStyle={{
                borderStyle: 'solid',
                backgroundColor: '#eee'
              }}
              rejectStyle={{
                borderStyle: 'solid',
                backgroundColor: '#ffdddd'
              }}
            >
              <h2>Upload new case</h2>
              <div>Click here to choose a case to upload, or drag case here.</div>
            </Dropzone>
            {this.state.files.length > 0 ? <div>
              <h2>Uploading {this.state.files.length} files...</h2>
              <div>{this.state.files.map((file) => <img src={file.preview} /> )}</div>
            </div> : null}
          </div>
        </div>
      </div>
    );
  }
});

module.exports = React.createClass({
   render: function(){
     return (
       <VolumeBox url={volumeURL} pollInterval={2000} />
     );
   }
});