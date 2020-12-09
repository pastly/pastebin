from flask import render_template, request, redirect, url_for, abort,\
    current_app, send_file, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import UploadForm, PasteForm
from ..models import File, User, UserFile
from . import bp
from .. import db
from ..auth import anon_user
from tempfile import SpooledTemporaryFile
import os
import hashlib
import random

def hash_file(fd) -> str:
    fd.seek(0, 0)
    digest = hashlib.sha256(fd.read()).hexdigest()
    fd.seek(0, 0)
    return digest


# Given a hash, calculate the partial filename that the file should be stored
# at. If the hash is abcdef1111, then this returns a/b/c/d/abcdef1111
def fname_part(the_hash: str) -> str:
    return os.path.join(
        the_hash[0], the_hash[1], the_hash[2], the_hash[3], the_hash)


def rand_paste_fname_part() -> str:
    return 'paste-{}.txt'.format(current_app.hashids.encode(
        random.getrandbits(32)))


# Check if we have a row in the File table with the given hash. If so, return
# it. Else return None
def have_file(the_hash):
    return File.query.filter_by(hash=the_hash).first()


# Check if we have a row in the UserFile table with the given User and File. If
# so, return it, else None
def have_userfile(dbuser, dbfile):
    return UserFile.query.filter_by(user_id=dbuser.id, file_id=dbfile.id)\
        .first()


def store_file(dbuser, fd, user_fname, is_binary, is_anon):
    the_hash = hash_file(fd)
    # Check for an existing File row
    existing_dbfile = have_file(the_hash)
    if existing_dbfile:
        # Someone already uploaded a file that hashes to this. See if it
        # was the current user (where the current user could be
        # the anonymous user)
        existing_dbuserfile = have_userfile(dbuser, existing_dbfile)
        if existing_dbuserfile:
            # Yes it was the current user. Don't need to do anything.
            you = 'Anonymous' if is_anon else 'You'
            flash(f'{you} already uploaded/pasted that')
        else:
            # No it wasn't the current user. Add a UserFile row showing that
            # this user also uploaded this file.
            db.session.add(UserFile(
                user_id=dbuser.id,
                file_id=existing_dbfile.id,
                fname=user_fname))
            db.session.commit()
        # Done and redirect to showing the page for this file.
        return redirect(url_for(
            'file.index_one',
            user_id_hash=current_app.hashids.encode(dbuser.id),
            file_id_hash=current_app.hashids.encode(existing_dbfile.id)))
    # This is a new file, so need to save it.
    fname = os.path.join(
        current_app.config['STORAGE'], fname_part(the_hash))
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    with open(fname, 'wb' if is_binary else 'wt') as fd_out:
        fd_out.write(fd.read())
    # Add a File row.
    db.session.add(File(hash=the_hash))
    db.session.commit()
    # And a UserFile row.
    dbfile = File.query.filter_by(hash=the_hash).first()
    db.session.add(UserFile(
        user_id=dbuser.id,
        file_id=dbfile.id,
        fname=user_fname))
    db.session.commit()
    # Done and redirect to the page for this file.
    return redirect(url_for(
        'file.index_one',
        user_id_hash=current_app.hashids.encode(dbuser.id),
        file_id_hash=current_app.hashids.encode(dbfile.id),
    ))


# Route for a signed-in user to upload a file non-anonymously
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    return _upload(current_user, UploadForm(), is_anon=False)


# Router for anyone (even a signed-in user) to upload a file anonymously
@bp.route('/upload/anon', methods=['GET', 'POST'])
def upload_anon():
    return _upload(anon_user(), UploadForm(), is_anon=True)


# Actually do the file upload route GET or POST.
def _upload(dbuser, form, is_anon):
    if form.validate_on_submit():
        return store_file(
            dbuser, form.f.data, form.f.data.filename, True, is_anon)
    # GET instead of POST. Show the form.
    if is_anon:
        title = 'Upload file anonymously'
    else:
        title = 'Upload file'
    return render_template(
        'file/upload.html', form=form, title=title)


@bp.route('/paste', methods=['GET', 'POST'])
@login_required
def paste():
    return _paste(current_user, PasteForm(), is_anon=False)


@bp.route('/paste/anon', methods=['GET', 'POST'])
def paste_anon():
    return _paste(anon_user(), PasteForm(), is_anon=True)


def _paste(dbuser, form, is_anon):
    if form.validate_on_submit():
        with SpooledTemporaryFile(max_size=10000, mode='wb') as fd:
            fd.write(form.t.data.encode('utf-8'))
            fd.seek(0, 0)
            fname = form.fname.data if form.fname.data else \
                rand_paste_fname_part()
            return store_file(dbuser, fd, fname, True, is_anon)
    # GET instead of POST. Show the form.
    if is_anon:
        title = 'Paste text anonymously'
    else:
        title = 'Paste text'
    return render_template(
        'file/paste.html', form=form, title=title)


@bp.route('/<user_id_hash>/<file_id_hash>/delete', methods=['GET'])
@login_required
def delete(user_id_hash, file_id_hash):
    # Decode the IDs and return early if fake
    user_id_int = idhash_to_id(user_id_hash)
    file_id_int = idhash_to_id(file_id_hash)
    if user_id_int is None or file_id_int is None:
        abort(404)
    # If user id is not current user, return early
    if user_id_int != current_user.id:
        abort(401)
    dbuserfile = UserFile.query.filter_by(
        user_id=user_id_int,
        file_id=file_id_int).first()
    if not dbuserfile:
        abort(404)
    db.session.delete(dbuserfile)
    db.session.commit()
    # XXX TODO check if anyone else has uploaded the file, and if not, delete
    # it from disk and the File table.
    return redirect(url_for('profile.index'))


# Try to convert a hashids hash into the int it represetns. If we can't return
# None. If it decodes to a tuple (because that's possible with hashids, but we
# don't use that) return None. Else return the int.
def idhash_to_id(s: str):
    # this returns a tuple
    i = current_app.hashids.decode(s)
    # 0 len if invalid hashid, >1 if hashid for a 2+ len tuple
    if len(i) != 1:
        return None
    return i[0]


# The information page for a specific file as uploaded by a specifc user.
# Contains download links and the filename the user used when uploading.
@bp.route('/<user_id_hash>/<file_id_hash>', methods=['GET'])
def index_one(user_id_hash, file_id_hash):
    # Decode the IDs and return early if fake
    user_id_int = idhash_to_id(user_id_hash)
    file_id_int = idhash_to_id(file_id_hash)
    if user_id_int is None or file_id_int is None:
        abort(404)
    # Get the File, User, and UserFile info, or return early if any of it is
    # missing.
    result = db.session.query(UserFile, User, File)\
        .filter(UserFile.user_id == user_id_int)\
        .filter(UserFile.file_id == file_id_int)\
        .filter(User.id == user_id_int)\
        .filter(File.id == file_id_int)\
        .first()
    if not result:
        abort(404)
    dbuserfile, dbuser, dbfile = result
    # Don't need to calculate these, since we got them from the path
    # user_id_hash=current_app.hashids.encode(dbuser.id)
    # file_id_hash=current_app.hashids.encode(dbfile.id)
    return render_template(
        'file/show.html',
        userfile=dbuserfile, user=dbuser, file=dbfile,
        download_url=url_for(
            'file.download',
            user_id_hash=user_id_hash, file_id_hash=file_id_hash),
        show_url=url_for(
            'file.show',
            user_id_hash=user_id_hash, file_id_hash=file_id_hash),
        plain_url=url_for(
            'file.plain',
            user_id_hash=user_id_hash, file_id_hash=file_id_hash),
        delete_url=url_for(
            'file.delete',
            user_id_hash=user_id_hash, file_id_hash=file_id_hash),
    )

# Helper for downloading/showing a file, as the operations are very similar.
#
# as_attachment: the response should have 'Content-Disposition: attachment' and
# a friendly filename.
# as_plain: the response should have mimetype of 'text/plain' so browsers will
# show it instead of prompt to download it.
#
# It doesn't make sense to specify both as_attachment and as_plain, but it is
# fine to specify neither.
def dl_or_show(user_id_hash, file_id_hash, as_attachment, as_plain):
    # decode the IDs and return early if can't
    user_id_int = idhash_to_id(user_id_hash)
    file_id_int = idhash_to_id(file_id_hash)
    if user_id_int is None or file_id_int is None:
        abort(404)
    # Try to get the File, User, and UserFile, and return early if can't
    result = db.session.query(UserFile, User, File)\
        .filter(UserFile.user_id == user_id_int)\
        .filter(UserFile.file_id == file_id_int)\
        .filter(User.id == user_id_int)\
        .filter(File.id == file_id_int)\
        .first()
    if not result:
        abort(404)
    dbuserfile, dbuser, dbfile = result
    # Path to file on disk.
    fname = os.path.join(
        current_app.config['STORAGE'], fname_part(dbfile.hash))
    return send_file(
        fname,
        mimetype='text/plain' if as_plain else None,
        as_attachment=as_attachment,
        attachment_filename=dbuserfile.fname,
        conditional=True,
    )


# Route for prompting to download the file with a friendly name
@bp.route('/<user_id_hash>/<file_id_hash>/download', methods=['GET'])
def download(user_id_hash, file_id_hash):
    return dl_or_show(
        user_id_hash, file_id_hash, as_attachment=True, as_plain=False)


# Route for showing a file with the best-guess mimetype. PDFs and images should
# render in the browser. HTML will also render in the browser, which maybe is
# dangerous?
@bp.route('/<user_id_hash>/<file_id_hash>/show', methods=['GET'])
def show(user_id_hash, file_id_hash):
    return dl_or_show(
        user_id_hash, file_id_hash, as_attachment=False, as_plain=False)


# Route for showing a file with 'text/plain' mimetype. Plain text files and
# scripts and pastes will find this useful. This is also how to show HTML
# content as opposed to render it.
@bp.route('/<user_id_hash>/<file_id_hash>/plain', methods=['GET'])
def plain(user_id_hash, file_id_hash):
    return dl_or_show(
        user_id_hash, file_id_hash, as_attachment=False, as_plain=True)
