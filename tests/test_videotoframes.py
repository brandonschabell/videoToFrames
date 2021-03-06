import cv2
import os
import pytest
import shutil

from videotoframes import get_frames_to_grab
from videotoframes.video_to_frames import main

from tests.utilities import get_testfiles_path


def test_main_no_arguments(capsys):
	with pytest.raises(SystemExit):
		main()
	captured = capsys.readouterr()
	assert 'videotoframes: error: the following arguments are required: -o, -i' in captured[1]


def test_main_no_output(capsys):
	with pytest.raises(SystemExit):
		main(['-i', './'])
	captured = capsys.readouterr()
	assert 'videotoframes: error: the following arguments are required: -o\n' in captured[1]


def test_main_no_input(capsys):
	with pytest.raises(SystemExit):
		main(['-o', './'])
	captured = capsys.readouterr()
	assert 'videotoframes: error: the following arguments are required: -i\n' in captured[1]


def test_main(tmpdir):
	main(['-i', os.path.join(get_testfiles_path(), 'small.mp4'), '-o', os.path.join(str(tmpdir), 'frames')])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	assert len(frames) == 166


def test_main_max_frames(tmpdir):
	main(['-i', os.path.join(get_testfiles_path(), 'small.mp4'),
	      '-o', os.path.join(str(tmpdir), 'frames'),
	      '--max-frames=10'])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	assert len(frames) == 10
	expected_frames = ['small-frame{:03d}.jpg'.format(i) for i in range(0, 10)]
	assert set(frames) == set(expected_frames)


def test_main_max_frames_even(tmpdir):
	main(['-i', os.path.join(get_testfiles_path(), 'small.mp4'),
	      '-o', os.path.join(str(tmpdir), 'frames'),
	      '--max-frames=10',
	      '--even'])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	assert len(frames) == 10
	assert 'small-frame000.jpg' in frames
	assert 'small-frame165.jpg' in frames


def test_main_max_frames_even_2_frames(tmpdir):
	main(['-i', os.path.join(get_testfiles_path(), 'small.mp4'),
	      '-o', os.path.join(str(tmpdir), 'frames'),
	      '--max-frames=2',
	      '--even'])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	assert len(frames) == 2
	expected_frames = ['small-frame{:03d}.jpg'.format(i) for i in [0, 165]]
	assert set(frames) == set(expected_frames)


def test_main_frame_content(tmpdir):
	main(['-i', os.path.join(get_testfiles_path(), 'small.mp4'),
	      '-o', os.path.join(str(tmpdir), 'frames'),
	      '--max-frames=1'])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	frame_path = os.path.join(str(tmpdir), 'frames', frames[0])
	image = cv2.imread(frame_path)
	assert image is not None
	assert image.shape == (320, 560, 3)


def test_frame_grabber_2_frames_even():
	frames = get_frames_to_grab(frame_count=10, max_frames=2)
	assert sorted(frames) == [0, 9]


def test_frame_grabber_3_frames_even():
	frames = get_frames_to_grab(frame_count=10, max_frames=3)
	assert sorted(frames) == [0, 4, 9]


def test_frame_grabber_4_frames_even():
	frames = get_frames_to_grab(frame_count=10, max_frames=4)
	assert sorted(frames) == [0, 3, 6, 9]


def test_frame_grabber_6_frames_even():
	frames = get_frames_to_grab(frame_count=10, max_frames=6)
	assert sorted(frames) == [0, 2, 4, 5, 7, 9]


def test_frame_grabber_2_frames_odd():
	frames = get_frames_to_grab(frame_count=11, max_frames=2)
	assert sorted(frames) == [0, 10]


def test_frame_grabber_3_frames_odd():
	frames = get_frames_to_grab(frame_count=11, max_frames=3)
	assert sorted(frames) == [0, 5, 10]


def test_frame_grabber_4_frames_odd():
	frames = get_frames_to_grab(frame_count=11, max_frames=4)
	assert sorted(frames) == [0, 3, 7, 10]


def test_frame_grabber_6_frames_odd():
	frames = get_frames_to_grab(frame_count=11, max_frames=6)
	assert sorted(frames) == [0, 2, 4, 6, 8, 10]


def test_multiple_videos(tmpdir):
	shutil.copyfile(os.path.join(get_testfiles_path(), 'small.mp4'), os.path.join(str(tmpdir), 'small.mp4'))
	shutil.copyfile(os.path.join(get_testfiles_path(), 'small.mp4'), os.path.join(str(tmpdir), 'small2.mp4'))
	main(['-i', os.path.join(str(tmpdir)),
	      '-o', os.path.join(str(tmpdir), 'frames')])
	frames = os.listdir(os.path.join(str(tmpdir), 'frames'))
	assert len(frames) == 332


def test_empty_input(tmpdir):
	tmpdir.mkdir('empty')
	with pytest.raises(Exception, match='No video selected.') as e:
		main(['-i', os.path.join(str(tmpdir), 'empty'),
		      '-o', os.path.join(str(tmpdir), 'frames')])
