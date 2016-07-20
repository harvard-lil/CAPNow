import 'stylesheets/app'

var React = require('react');
var Dropzone = require('react-dropzone');
var request = require('superagent');
require('superagent-django-csrf');

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
    <div>
      <div className="col-sm-2">{ proof ? <a href={proof.docx}>download proof .docx</a> : "" }</div>
      <div className="col-sm-2">
        { proof ?
            proof.pdf_status == "generated" ?
              <a href={proof.pdf}>download proof .pdf</a> :
            proof.pdf_status == "pending" ?
              "PDF generating" :
              "Generating PDF failed" :
            ""
        }
      </div>
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
    </div>
  );
}

var VolumeBox = React.createClass({
  loadVolumesFromServer: function() {
    request.get(this.props.url)
      .end((err, res)=>{
      if(!err){
        this.loadInterval && this.setState({data: res.body});
      }
    });
  },
  updateStateData: (data) => {
    this.setState({data: data})
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
  endpointURL: function(){
    return volumeURL+this.props.data.id+"/";
  },

  generateFrontMatter: function(){
    request.post(this.endpointURL()+"front_matter_proofs/")
      .end();
  },

  exportVolume: function(){
    window.open(this.endpointURL()+"export/", "_blank");
  },

  render: function() {
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
});

var Case = React.createClass({
  endpointURL: function(){
    return createCaseURL+this.props.data.id+"/";
  },

  onPublish: function(){
    var oldState = this.state.status;
    this.setState({status: "published"});
    request.patch(this.endpointURL())
      .send({status: "published"})
      .end((err, res)=>{
        if(err){
          this.setState({status: oldState});
        }
      });
  },

  getInitialState: function () {
			return {status: this.props.data.status};
  },

  render: function() {
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
          <div className="col-sm-2">{
            this.state.status == "draft" ?
              <button className="btn btn-sm btn-outline-primary" onClick={this.onPublish}>Publish</button> :
              this.state.status
          }</div>
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
    request.post(createCaseURL)
      .attach("manuscript", files[0])
      .end();
  },

  render: function () {
    return (
      <div className="caseForm">

        <div className="row">
          <div className="col-lg-12" style={{padding:'3em'}}>
            <Dropzone
              ref="dropzone"
              onDrop={this.onDrop}
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