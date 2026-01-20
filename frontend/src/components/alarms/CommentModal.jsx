import React from 'react';
import { Plus, X } from 'lucide-react';

const CommentModal = ({
    show,
    selectedCommentAlert,
    isAddingComment,
    setIsAddingComment,
    newCommentText,
    setNewCommentText,
    commentUpdateLoading,
    formatTimestamp,
    onAddComment,
    onClose
}) => {
    if (!show || !selectedCommentAlert) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-container" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">Alert Comment</h2>
                    <button 
                        className="modal-close"
                        onClick={onClose}
                    >
                        <X size={24} />
                    </button>
                </div>

                <div className="rule-form">
                    <div className="form-group form-group-full">
                        <label className="form-label">Alert Rule</label>
                        <div style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                            {selectedCommentAlert.alert_rule?.name || 'No name'}
                        </div>
                    </div>

                    <div className="form-group form-group-full">
                        <label className="form-label">Existing Comment</label>
                        <div style={{ 
                            padding: '12px', 
                            background: 'rgba(255, 255, 255, 0.05)', 
                            border: '1px solid var(--border-color)',
                            borderRadius: '6px',
                            minHeight: '100px',
                            whiteSpace: 'pre-wrap',
                            wordWrap: 'break-word',
                            opacity: 0.8
                        }}>
                            {selectedCommentAlert.alert_comment?.text || 'No comment'}
                        </div>
                    </div>

                    {isAddingComment && (
                        <div className="form-group form-group-full">
                            <label className="form-label">Add New Comment Part</label>
                            <textarea
                                className="form-input"
                                value={newCommentText}
                                onChange={(e) => setNewCommentText(e.target.value)}
                                placeholder="Enter a new comment part..."
                                rows="6"
                                style={{ resize: 'vertical' }}
                            />
                        </div>
                    )}

                    <div className="form-group form-group-full">
                        <label className="form-label">Comment Timestamp</label>
                        <div style={{ padding: '8px 12px', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid var(--border-color)', borderRadius: '6px' }}>
                            {formatTimestamp(selectedCommentAlert.alert_comment?.timestamp)}
                        </div>
                    </div>

                    <div className="form-actions">
                        {!isAddingComment ? (
                            <>
                                <button
                                    type="button"
                                    className="btn-secondary"
                                    onClick={() => setIsAddingComment(true)}
                                >
                                    <Plus size={16} style={{ marginRight: '8px' }} />
                                    Add Comment
                                </button>
                                <button
                                    type="button"
                                    className="btn-primary"
                                    onClick={onClose}
                                >
                                    Close
                                </button>
                            </>
                        ) : (
                            <>
                                <button
                                    type="button"
                                    className="btn-secondary"
                                    onClick={() => {
                                        setIsAddingComment(false);
                                        setNewCommentText('');
                                    }}
                                    disabled={commentUpdateLoading}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="button"
                                    className="btn-primary"
                                    onClick={onAddComment}
                                    disabled={commentUpdateLoading || !newCommentText.trim()}
                                >
                                    {commentUpdateLoading ? 'Saving...' : 'Save'}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CommentModal;
