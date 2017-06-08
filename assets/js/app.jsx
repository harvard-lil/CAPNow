import 'stylesheets/app'

var React = require('react');
var Dropzone = require('react-dropzone');
var request = require('superagent');
require('superagent-django-csrf');
import update from 'immutability-helper';

// monkey-patch request with universal settings
var _request_end = request.Request.prototype.end;
request.Request.prototype.end = function(fn) {
  this.accept('json');
  return _request_end.call(this, function(err, res){
    if(err){
      console.log("Error submitting case: ", err)
    }
    if(fn)
      fn(err, res);
  });
};

function getProofDivs(proof, onDropURL){
  function onDrop(files){
    request.post(onDropURL)
      .attach("docx", files[0])
      .end();
  }

  return (
    [
      <div className="col-sm-2">{ (proof && proof.docx) ? <a href={proof.docx}>download proof .docx</a> : "" }</div>,
      //<div className="col-sm-2">{ (proof && proof.xml) ? <a href={proof.xml}>download proof .xml</a> : "" }</div>,
      //<div className="col-sm-2">{ (proof && proof.html) ? <a href={proof.html}>download proof .html</a> : "" }</div>,
      <div className="col-sm-2">
        { proof ?
            proof.pdf_status == "generated" ?
              <a href={proof.pdf}>download proof .pdf</a> :
            proof.pdf_status == "pending" ?
              "PDF generating" :
              "Generating PDF failed" :
            ""
        }
      </div>,
      <div className="col-sm-2">
        <Dropzone
          ref="dropzone"
          onDrop={onDrop}
          multiple={false}
          accept="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          disablePreview={true}
          className="drop-target drop-target-small"
          activeClassName="drop-target-active"
          rejectClassName="drop-target-rejected"
        >
          <p>Replace proof</p>
        </Dropzone>
      </div>
    ]
  );
}

function updateState(component, changes){
  // see https://github.com/kolodny/immutability-helper#available-commands for format of `changes`
  component.setState(update(component.state, changes));
}

class VolumeBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {data: []};
  }

  loadVolumesFromServer = () =>  {
    request.get(this.props.url)
      .end((err, res)=>{
      if(!err){
        this.loadInterval && updateState(this, {data: {$set: res.body}});
      }
    });
  }

  componentDidMount = () => {
    this.loadVolumesFromServer();
    this.loadInterval = setInterval(this.loadVolumesFromServer.bind(this), this.props.pollInterval);
  }
  componentWillUnmount = () => {
      this.loadInterval && clearInterval(this.loadInterval);
      this.loadInterval = false;
  }
  render() {
    return (
      <div className="volumeBox">
        <CaseForm />

        <VolumeList data={this.state.data} />
      </div>
    );
  }
}

class VolumeList extends React.Component {
  render() {
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
}

class Volume extends React.Component {
  endpointURL = () => {
    return volumeURL+this.props.data.id+"/";
  }

  generateFrontMatter = () => {
    request.post(this.endpointURL()+"front_matter_proofs/")
      .end();
  }

  exportVolume = () => {
    window.open(this.endpointURL()+"export/", "_blank");
  }

  render() {
    var caseNodes = this.props.data.cases.map(function(caseData) {
      return (
        <Case key={caseData.id} data={caseData}/>
      );
    });
    var frontMatter = this.props.data.front_matter_proofs[0];
    return (
      <div className="volume">
        <div className="row">
          <div className="col-lg-12">
            <h4>{this.props.data.volume_number} {this.props.data.series}</h4>
            <div className="volume-sub-row">
              <div className="row">
                <div className="col-sm-12">
                  <button className="btn btn-sm btn-outline-primary" onClick={this.exportVolume}>Export as Book</button>
                </div>
              </div>
            </div>

            <div className="front-matter volume-sub-row">
              <div className="row">
                <div className="col-sm-12"><h5>Front Matter</h5></div>
              </div>
              <div className="row">
                <div className="col-sm-2">
                  <button className="btn btn-sm btn-outline-primary" onClick={this.generateFrontMatter}>{ frontMatter ? "Regenerate" : "Generate" }</button>
                </div>

                {
                  frontMatter ?
                    getProofDivs(frontMatter, this.endpointURL()+"front_matter_proofs/") :
                    ""
                }
              </div>
            </div>

            {caseNodes}
          </div>
        </div>
      </div>
    );
  }
}

class Case extends React.Component {
  constructor(props) {
    super(props);
    this.state = {publication_status: this.props.data.publication_status};
  }

  endpointURL = () => {
    return createCaseURL+this.props.data.id+"/";
  }

  onPublish = () => {
    var oldState = this.state;
    this.setState({publication_status: "published"});
    request.patch(this.endpointURL())
      .send({publication_status: "published"})
      .end((err, res)=>{
        if(err){
          this.setState({publication_status: oldState});
        }
      });
  }

  onDelete = () => {
    request.delete(this.endpointURL())
      .send()
      .end();
  }

  render() {
    var d = this.props.data;
    var proof = d.proofs[0];
    return (
      <div className="case volume-sub-row">
        <div className="row">
          <div className="col-sm-12"><h5>{d.citation}</h5></div>
        </div>
        <div className="row">
          <div className="col-sm-2"><a href={d.manuscript}>download manuscript</a></div>
          {getProofDivs(proof, this.endpointURL()+"proofs/")}
          <div className="col-sm-1">{
            this.state.publication_status == "draft" ?
              <button className="btn btn-sm btn-outline-primary" onClick={this.onPublish}>Publish</button> :
              this.state.publication_status
          }</div>
          <div className="col-sm-1"><button className="btn btn-sm btn-outline-danger" onClick={this.onDelete.bind(this)}>Delete</button></div>
        </div>
      </div>
    );
  }
}

class CaseForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {files: []};
    console.log("0", this.props);
  }

  setErrorMessage = (message) => {
    updateState(this, {errorMessage: {$set: message}});
  }

  onDrop = (files) => {
    this.setErrorMessage(null);
    request.post(createCaseURL)
      .attach("manuscript", files[0])
      .end((err, res) => {
        if(err){
          this.setErrorMessage("Error uploading case: "+res.body.non_field_errors[0]);
        }
      });
  }

  onCloseMessage = () => {
    this.setErrorMessage(null);
  }

  render() {
    return (
      <div className="caseForm">

        <div className="row">
          <div className="col-lg-12" style={{padding:'3em'}}>
            <Dropzone
              ref="dropzone"
              onDrop={this.onDrop.bind(this)}
              multiple={false}
              accept="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              disablePreview={true}
              className="drop-target"
              activeClassName="drop-target-active"
              rejectClassName="drop-target-rejected"
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

        {
          this.state.errorMessage ?
            <div className="row">
              <div className="alert alert-danger alert-dismissible fade show w-100" role="alert">
                <button type="button" className="close" onClick={this.onCloseMessage.bind(this)} data-dismiss="alert" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
                {this.state.errorMessage}
              </div>
            </div>
            : ""
        }
      </div>
    );
  }
}

module.exports = function(props) {
  return (
    <VolumeBox url={volumeURL} pollInterval={2000}/>
  );
}
